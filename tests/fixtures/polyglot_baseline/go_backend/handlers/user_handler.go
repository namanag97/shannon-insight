package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	"backend/models"
	"backend/services"

	"github.com/gorilla/mux"
)

type UserHandler struct {
	userService *services.UserService
}

func NewUserHandler(userService *services.UserService) *UserHandler {
	return &UserHandler{
		userService: userService,
	}
}

func (h *UserHandler) ListUsers(w http.ResponseWriter, r *http.Request) {
	users, err := h.userService.GetAllUsers(r.Context())
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to list users: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"data":  users,
		"count": len(users),
	})
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid user id")
		return
	}

	user, err := h.userService.GetUserByID(r.Context(), userID)
	if err != nil {
		if err == models.ErrUserNotFound {
			respondWithError(w, http.StatusNotFound, "user not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to get user: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, user)
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Name     string `json:"name"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.Email == "" || req.Password == "" || req.Name == "" {
		respondWithError(w, http.StatusBadRequest, "missing required fields")
		return
	}

	user := &models.User{
		Email: req.Email,
		Name:  req.Name,
	}

	if err := user.SetPassword(req.Password); err != nil {
		respondWithError(w, http.StatusInternalServerError, "failed to hash password")
		return
	}

	created, err := h.userService.CreateUser(r.Context(), user)
	if err != nil {
		if err == models.ErrUserAlreadyExists {
			respondWithError(w, http.StatusConflict, "user already exists")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to create user: %v", err))
		return
	}

	respondWithJSON(w, http.StatusCreated, created)
}

func (h *UserHandler) UpdateUser(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid user id")
		return
	}

	var req struct {
		Name string `json:"name"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	user, err := h.userService.UpdateUser(r.Context(), userID, req.Name)
	if err != nil {
		if err == models.ErrUserNotFound {
			respondWithError(w, http.StatusNotFound, "user not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to update user: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, user)
}

func (h *UserHandler) DeleteUser(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	userID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid user id")
		return
	}

	if err := h.userService.DeleteUser(r.Context(), userID); err != nil {
		if err == models.ErrUserNotFound {
			respondWithError(w, http.StatusNotFound, "user not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to delete user: %v", err))
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(payload)
}

func respondWithError(w http.ResponseWriter, code int, message string) {
	respondWithJSON(w, code, map[string]string{"error": message})
}
