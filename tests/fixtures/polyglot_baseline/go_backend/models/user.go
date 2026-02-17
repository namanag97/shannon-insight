package models

import (
	"time"

	"backend/utils"
)

type User struct {
	ID           int64     `json:"id"`
	Email        string    `json:"email"`
	Name         string    `json:"name"`
	PasswordHash string    `json:"-"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	LastLogin    *time.Time `json:"last_login,omitempty"`
	IsActive     bool      `json:"is_active"`
}

func (u *User) SetPassword(password string) error {
	hash, err := utils.HashPassword(password)
	if err != nil {
		return err
	}
	u.PasswordHash = hash
	return nil
}

func (u *User) VerifyPassword(password string) bool {
	return utils.VerifyPassword(u.PasswordHash, password)
}

func NewUser(email, name, password string) (*User, error) {
	user := &User{
		Email:     email,
		Name:      name,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
		IsActive:  true,
	}

	if err := user.SetPassword(password); err != nil {
		return nil, err
	}

	return user, nil
}
