package services

import (
	"context"
	"fmt"
	"strings"

	"backend/models"
	"backend/repository"
)

type OrgService struct {
	repo repository.OrgRepository
}

func NewOrgService(repo repository.OrgRepository) *OrgService {
	return &OrgService{repo: repo}
}

func (s *OrgService) GetAllOrgs(ctx context.Context) ([]*models.Organization, error) {
	orgs, err := s.repo.GetAll(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get all organizations: %w", err)
	}
	return orgs, nil
}

func (s *OrgService) GetOrgByID(ctx context.Context, id int64) (*models.Organization, error) {
	org, err := s.repo.GetByID(ctx, id)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return nil, models.ErrOrgNotFound
		}
		return nil, fmt.Errorf("failed to get organization by id: %w", err)
	}
	return org, nil
}

func (s *OrgService) GetOrgByName(ctx context.Context, name string) (*models.Organization, error) {
	if name == "" {
		return nil, fmt.Errorf("organization name cannot be empty")
	}

	org, err := s.repo.GetByName(ctx, name)
	if err != nil {
		if strings.Contains(err.Error(), "not found") {
			return nil, models.ErrOrgNotFound
		}
		return nil, fmt.Errorf("failed to get organization by name: %w", err)
	}
	return org, nil
}

func (s *OrgService) CreateOrg(ctx context.Context, org *models.Organization) (*models.Organization, error) {
	if org.Name == "" {
		return nil, fmt.Errorf("organization name is required")
	}

	created, err := s.repo.Create(ctx, org)
	if err != nil {
		return nil, fmt.Errorf("failed to create organization: %w", err)
	}

	return created, nil
}

func (s *OrgService) UpdateOrg(ctx context.Context, id int64, name, description string) (*models.Organization, error) {
	if name == "" {
		return nil, fmt.Errorf("organization name cannot be empty")
	}

	existing, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, models.ErrOrgNotFound
	}

	existing.Name = name
	existing.Description = description

	updated, err := s.repo.Update(ctx, existing)
	if err != nil {
		return nil, fmt.Errorf("failed to update organization: %w", err)
	}

	return updated, nil
}

func (s *OrgService) DeleteOrg(ctx context.Context, id int64) error {
	org, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return models.ErrOrgNotFound
	}

	if err := s.repo.Delete(ctx, org); err != nil {
		return fmt.Errorf("failed to delete organization: %w", err)
	}

	return nil
}
