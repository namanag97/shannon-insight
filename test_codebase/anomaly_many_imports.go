package main

import (
    "fmt"
    "strings"
    "os"
    "io"
    "bufio"
    "encoding/json"
    "encoding/xml"
    "net/http"
    "net/url"
    "time"
    "crypto/sha256"
    "crypto/md5"
)

func SwissArmyKnife() {
    fmt.Println(strings.ToUpper(os.Args[0]))
    var buf bytes.Buffer
    bufio.NewReader(os.Stdin)
    json.NewEncoder(os.Stdout)
    xml.NewDecoder(os.Stdin)
    http.Get("http://example.com")
    url.Parse("http://example.com")
    time.Now()
    sha256.New()
    md5.New()
}
