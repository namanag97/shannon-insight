package models

import "errors"

var (
	ErrUserNotFound      = errors.New("user not found")
	ErrUserAlreadyExists = errors.New("user already exists")
	ErrOrgNotFound       = errors.New("organization not found")
	ErrOrgAlreadyExists  = errors.New("organization already exists")
	ErrInvalidInput      = errors.New("invalid input provided")
	ErrUnauthorized      = errors.New("unauthorized access")
	ErrForbidden         = errors.New("forbidden access")
	ErrConflict          = errors.New("resource conflict")
	ErrInternalServer    = errors.New("internal server error")
	ErrNotImplemented    = errors.New("not implemented")
)
