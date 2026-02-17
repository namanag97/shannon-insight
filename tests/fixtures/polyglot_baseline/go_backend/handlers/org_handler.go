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

type OrgHandler struct {
	orgService *services.OrgService
}

func NewOrgHandler(orgService *services.OrgService) *OrgHandler {
	return &OrgHandler{
		orgService: orgService,
	}
}

func (h *OrgHandler) ListOrgs(w http.ResponseWriter, r *http.Request) {
	orgs, err := h.orgService.GetAllOrgs(r.Context())
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to list orgs: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, map[string]interface{}{
		"data":  orgs,
		"count": len(orgs),
	})
}

func (h *OrgHandler) GetOrg(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orgID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid org id")
		return
	}

	org, err := h.orgService.GetOrgByID(r.Context(), orgID)
	if err != nil {
		if err == models.ErrOrgNotFound {
			respondWithError(w, http.StatusNotFound, "organization not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to get org: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, org)
}

func (h *OrgHandler) CreateOrg(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Name        string `json:"name"`
		Description string `json:"description"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	if req.Name == "" {
		respondWithError(w, http.StatusBadRequest, "name is required")
		return
	}

	org := &models.Organization{
		Name:        req.Name,
		Description: req.Description,
	}

	created, err := h.orgService.CreateOrg(r.Context(), org)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to create org: %v", err))
		return
	}

	respondWithJSON(w, http.StatusCreated, created)
}

func (h *OrgHandler) UpdateOrg(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orgID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid org id")
		return
	}

	var req struct {
		Name        string `json:"name"`
		Description string `json:"description"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid request body")
		return
	}

	org, err := h.orgService.UpdateOrg(r.Context(), orgID, req.Name, req.Description)
	if err != nil {
		if err == models.ErrOrgNotFound {
			respondWithError(w, http.StatusNotFound, "organization not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to update org: %v", err))
		return
	}

	respondWithJSON(w, http.StatusOK, org)
}

func (h *OrgHandler) DeleteOrg(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orgID, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid org id")
		return
	}

	if err := h.orgService.DeleteOrg(r.Context(), orgID); err != nil {
		if err == models.ErrOrgNotFound {
			respondWithError(w, http.StatusNotFound, "organization not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, fmt.Sprintf("failed to delete org: %v", err))
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
