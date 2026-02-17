package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"backend/config"
	"backend/handlers"
	"backend/models"
	"backend/repository"
	"backend/services"
	"backend/utils"

	"github.com/gorilla/mux"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("failed to load config: %v", err)
	}

	userRepo := repository.NewUserRepository(cfg.DatabaseURL)
	orgRepo := repository.NewOrgRepository(cfg.DatabaseURL)

	authService := services.NewAuthService(cfg.JWTSecret)
	userService := services.NewUserService(userRepo)
	orgService := services.NewOrgService(orgRepo)

	userHandler := handlers.NewUserHandler(userService)
	orgHandler := handlers.NewOrgHandler(orgService)
	authHandler := handlers.NewAuthHandler(authService, userService)

	router := mux.NewRouter()

	router.Use(handlers.LoggingMiddleware)
	router.Use(handlers.CORSMiddleware)

	api := router.PathPrefix("/api/v1").Subrouter()
	api.Use(handlers.AuthMiddleware(authService))

	api.HandleFunc("/users", userHandler.ListUsers).Methods("GET")
	api.HandleFunc("/users", userHandler.CreateUser).Methods("POST")
	api.HandleFunc("/users/{id}", userHandler.GetUser).Methods("GET")
	api.HandleFunc("/users/{id}", userHandler.UpdateUser).Methods("PUT")
	api.HandleFunc("/users/{id}", userHandler.DeleteUser).Methods("DELETE")

	api.HandleFunc("/organizations", orgHandler.ListOrgs).Methods("GET")
	api.HandleFunc("/organizations", orgHandler.CreateOrg).Methods("POST")
	api.HandleFunc("/organizations/{id}", orgHandler.GetOrg).Methods("GET")
	api.HandleFunc("/organizations/{id}", orgHandler.UpdateOrg).Methods("PUT")
	api.HandleFunc("/organizations/{id}", orgHandler.DeleteOrg).Methods("DELETE")

	authRouter := router.PathPrefix("/auth").Subrouter()
	authRouter.Use(handlers.CORSMiddleware)
	authRouter.HandleFunc("/login", authHandler.Login).Methods("POST")
	authRouter.HandleFunc("/logout", authHandler.Logout).Methods("POST")
	authRouter.HandleFunc("/refresh", authHandler.RefreshToken).Methods("POST")

	server := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	go func() {
		log.Printf("starting server on %s", server.Addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Printf("shutdown error: %v", err)
	}

	log.Println("server stopped")
}
