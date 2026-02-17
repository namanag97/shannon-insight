package services

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type AuthService struct {
	jwtSecret string
}

type Claims struct {
	UserID int64 `json:"user_id"`
	jwt.RegisteredClaims
}

func NewAuthService(jwtSecret string) *AuthService {
	if jwtSecret == "" {
		jwtSecret = "default-secret-key-change-in-production"
	}
	return &AuthService{jwtSecret: jwtSecret}
}

func (s *AuthService) GenerateToken(userID int64) (string, error) {
	expirationTime := time.Now().Add(1 * time.Hour)

	claims := &Claims{
		UserID: userID,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expirationTime),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := token.SignedString([]byte(s.jwtSecret))
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return tokenString, nil
}

func (s *AuthService) ValidateToken(tokenString string) (int64, error) {
	claims := &Claims{}

	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(s.jwtSecret), nil
	})

	if err != nil {
		return 0, fmt.Errorf("failed to parse token: %w", err)
	}

	if !token.Valid {
		return 0, fmt.Errorf("invalid token")
	}

	if claims.ExpiresAt != nil && claims.ExpiresAt.Before(time.Now()) {
		return 0, fmt.Errorf("token expired")
	}

	return claims.UserID, nil
}
