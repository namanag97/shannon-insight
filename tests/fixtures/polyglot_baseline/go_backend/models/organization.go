package models

import "time"

type Organization struct {
	ID          int64     `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	OwnerID     int64     `json:"owner_id"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	IsActive    bool      `json:"is_active"`
}

type OrgMember struct {
	ID     int64  `json:"id"`
	OrgID  int64  `json:"org_id"`
	UserID int64  `json:"user_id"`
	Role   string `json:"role"` // admin, member, viewer
	AddedAt time.Time `json:"added_at"`
}

func NewOrganization(name, description string, ownerID int64) *Organization {
	return &Organization{
		Name:        name,
		Description: description,
		OwnerID:     ownerID,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
		IsActive:    true,
	}
}
