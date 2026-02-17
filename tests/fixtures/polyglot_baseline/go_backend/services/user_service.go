package services

import (
	"context"
	"fmt"
	"strings"

	"backend/models"
	"backend/repository"
)

type UserService struct {
	repo repository.UserRepository
}

func NewUserService(repo repository.UserRepository) *UserService {
	return &UserService{repo: repo}
}

func (s *UserService) GetAllUsers(ctx context.Context) ([]*models.User, error) {
	users, err := s.repo.GetAll(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get all users: %w", err)
	}
	return users, nil
}

func (s *UserService) GetUserByID(ctx context.Context, id int64) (*models.User, error) {
	user, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return nil, models.ErrUserNotFound
		}
		return nil, fmt.Errorf("failed to get user by id: %w", err)
	}
	return user, nil
}

func (s *UserService) GetUserByEmail(ctx context.Context, email string) (*models.User, error) {
	if email == "" {
		return nil, fmt.Errorf("email cannot be empty")
	}

	user, err := s.repo.GetByEmail(ctx, email)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return nil, models.ErrUserNotFound
		}
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}
	return user, nil
}

func (s *UserService) CreateUser(ctx context.Context, user *models.User) (*models.User, error) {
	if user.Email == "" || user.Name == "" {
		return nil, fmt.Errorf("email and name are required")
	}

	existing, err := s.repo.GetByEmail(ctx, user.Email)
	if err == nil && existing != nil {
		return nil, models.ErrUserAlreadyExists
	}

	created, err := s.repo.Create(ctx, user)
	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	return created, nil
}

func (s *UserService) UpdateUser(ctx context.Context, id int64, name string) (*models.User, error) {
	if name == "" {
		return nil, fmt.Errorf("name cannot be empty")
	}

	existing, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, models.ErrUserNotFound
	}

	existing.Name = name
	updated, err := s.repo.Update(ctx, existing)
	if err != nil {
		return nil, fmt.Errorf("failed to update user: %w", err)
	}

	return updated, nil
}

func (s *UserService) DeleteUser(ctx context.Context, id int64) error {
	user, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return models.ErrUserNotFound
	}

	if err := s.repo.Delete(ctx, user); err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}

	return nil
}
