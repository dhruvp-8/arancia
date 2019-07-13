package main

import (
	"fmt"
    "github.com/elazarl/goproxy"
    "log"
    "net/http"
)

func main() {
	proxy := goproxy.NewProxyHttpServer()
	proxy.Verbose = true
	proxy.OnRequest().DoFunc(
    func(r *http.Request,ctx *goproxy.ProxyCtx)(*http.Request,*http.Response) {
        fmt.Println(r.Method)
        return r,nil
    })
    log.Fatal(http.ListenAndServe(":7000", proxy))
}