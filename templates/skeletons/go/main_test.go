package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func novoHealthz() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})
	return mux
}

func TestHealthz(t *testing.T) {
	r := httptest.NewRequest("GET", "/healthz", nil)
	w := httptest.NewRecorder()
	novoHealthz().ServeHTTP(w, r)
	if w.Code != 200 {
		t.Fatalf("código %d, quer 200", w.Code)
	}
	var body map[string]string
	if err := json.Unmarshal(w.Body.Bytes(), &body); err != nil {
		t.Fatalf("json: %v", err)
	}
	if body["status"] != "ok" {
		t.Fatalf("body %v", body)
	}
}
