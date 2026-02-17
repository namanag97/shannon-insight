package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"

	"backend/models"
	"backend/services"
)

type AuthHandler struct {
	authService *services.AuthService
	userService *services.UserService
}

func NewAuthHandler(authService *services.AuthService, userService *services.UserService) *AuthHandler {
	return &AuthHandler{
		authService: authService,
		userService: userService,
	}
}

func (h *AuthHandler) Login(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.Email == "" || req.Password == "" {
		respondWithError(w, http.StatusBadRequest, "email and password required")
		return
	}

	user, err := h.userService.GetUserByEmail(r.Context(), req.Email)
	if err != nil {
		respondWithError(w, http.StatusUnauthorized, "invalid credentials")
		return
	}

	if !user.VerifyPassword(req.Password) {
		respondWithError(w, http.StatusUnauthorized, "invalid credentials")
		return
	}

	token, err := h.authService.GenerateToken(user.ID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "failed to generate token")
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"token":      token,
		"user_id":    user.ID,
		"email":      user.Email,
		"expires_in": 3600,
	})
}

func (h *AuthHandler) Logout(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"message": "logged out successfully",
	})
}

func (h *AuthHandler) RefreshToken(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Token string `json:"token"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	userID, err := h.authService.ValidateToken(req.Token)
	if err != nil {
		respondWithError(w, http.StatusUnauthorized, fmt.Sprintf("invalid token: %v", err))
		return
	}

	newToken, err := h.authService.GenerateToken(userID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "failed to generate new token")
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"token":      newToken,
		"expires_in": 3600,
	})
}
