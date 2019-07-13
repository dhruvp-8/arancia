package main

import (
	"fmt"
    "github.com/elazarl/goproxy"
    "log"
    "net/http"
)

func main() {
	fmt.Println("Hello, World!")
    proxy := goproxy.NewProxyHttpServer()
    proxy.Verbose = true
    log.Fatal(http.ListenAndServe(":7000", proxy))
}