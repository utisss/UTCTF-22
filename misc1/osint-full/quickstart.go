package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"google.golang.org/api/gmail/v1"
	"google.golang.org/api/option"
)

// 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
// Retrieve a token, saves the token, then returns the generated client.
func getClient(config *oauth2.Config) *http.Client {
	// The file token.json stores the user's access and refresh tokens, and is
	// created automatically when the authorization flow completes for the first
	// time.
	tokFile := "token.json"
	tok, err := tokenFromFile(tokFile)
	if err != nil {
		tok = getTokenFromWeb(config)
		saveToken(tokFile, tok)
	}
	return config.Client(context.Background(), tok)
}

// Request a token from the web, then returns the retrieved token.
func getTokenFromWeb(config *oauth2.Config) *oauth2.Token {
	authURL := config.AuthCodeURL("state-token", oauth2.AccessTypeOffline)
	fmt.Printf("Go to the following link in your browser then type the "+
		"authorization code: \n%v\n", authURL)

	var authCode string
	if _, err := fmt.Scan(&authCode); err != nil {
		log.Fatalf("Unable to read authorization code: %v", err)
	}

	tok, err := config.Exchange(context.TODO(), authCode)
	if err != nil {
		log.Fatalf("Unable to retrieve token from web: %v", err)
	}
	return tok
}

// Retrieves a token from a local file.
func tokenFromFile(file string) (*oauth2.Token, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	tok := &oauth2.Token{}
	err = json.NewDecoder(f).Decode(tok)
	return tok, err
}

// Saves a token to a file path.
func saveToken(path string, token *oauth2.Token) {
	fmt.Printf("Saving credential file to: %s\n", path)
	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatalf("Unable to cache oauth token: %v", err)
	}
	defer f.Close()
	json.NewEncoder(f).Encode(token)
}

func sendmail(srv gmail.Service, frommail string, mid string, user string) {
	temp := []byte("From: 'me'\r\n" +
		"reply-to: " + frommail + "\r\n" +
		"To:  " + frommail + "\r\n" +
		"Subject: Important CISO business \r\n" +
		"\r\nHi,\r\n" +
		"The flag is utflag{osint_is_fun}")

	var message gmail.Message

	message.Raw = base64.StdEncoding.EncodeToString(temp)
	message.Raw = strings.Replace(message.Raw, "/", "_", -1)
	message.Raw = strings.Replace(message.Raw, "+", "-", -1)
	message.Raw = strings.Replace(message.Raw, "=", "", -1)
	_, err := srv.Users.Messages.Send("me", &message).Do()
	if err != nil {
		log.Fatalf("Unable to send. %v", err)
	} else {
		_, err = srv.Users.Messages.Modify(user, mid, &gmail.ModifyMessageRequest{
			RemoveLabelIds: []string{"UNREAD"},
		}).Do()
	}
}

func sendwrongmail(srv gmail.Service, frommail string, mid string, user string) {
	temp := []byte("From: 'me'\r\n" +
		"reply-to: " + frommail + "\r\n" +
		"To:  " + frommail + "\r\n" +
		"Subject: Important CISO business \r\n" +
		"\r\nHi,\r\n" +
		"Something doesn't look quiet right")

	var message gmail.Message

	message.Raw = base64.StdEncoding.EncodeToString(temp)
	message.Raw = strings.Replace(message.Raw, "/", "_", -1)
	message.Raw = strings.Replace(message.Raw, "+", "-", -1)
	message.Raw = strings.Replace(message.Raw, "=", "", -1)
	_, err := srv.Users.Messages.Send("me", &message).Do()
	if err != nil {
		log.Fatalf("Unable to send. %v", err)
	} else {

		_, err = srv.Users.Messages.Modify(user, mid, &gmail.ModifyMessageRequest{
			RemoveLabelIds: []string{"UNREAD"},
		}).Do()
	}
}

func checkemail(contents string) bool {
	valid := true
	if !strings.Contains(contents, "factorio") && !strings.Contains(contents, "FactorIO") && !strings.Contains(contents, "Factorio") {
		valid = false
	}
	if !strings.Contains(contents, "spot") && !strings.Contains(contents, "Spot") {
		valid = false
	}
	if !strings.Contains(contents, "Texas A&amp;M") && !strings.Contains(contents, "Texas A&M") {
		valid = false
	}
	if !strings.Contains(contents, "CISO") && !strings.Contains(contents, "Chief Information Security Officer") && !strings.Contains(contents, "ciso") {
		valid = false
	}
	if !strings.Contains(contents, "Cacio e Pepe") && !strings.Contains(contents, "cacio e pepe") {
		valid = false
	}
	return valid

}

// https://developers.google.com/gmail/api/reference/rest/v1/users.messages/send
func main() {
	ctx := context.Background()
	b, err := ioutil.ReadFile("credentials.json")
	if err != nil {
		log.Fatalf("Unable to read client secret file: %v", err)
	}

	// If modifying these scopes, delete your previously saved token.json.
	config, err := google.ConfigFromJSON(b, gmail.MailGoogleComScope)
	if err != nil {
		log.Fatalf("Unable to parse client secret file to config: %v", err)
	}
	client := getClient(config)

	srv, err := gmail.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		log.Fatalf("Unable to retrieve Gmail client: %v", err)
	}

	user := "me"
	for i := 1; i < 130; i++ {
		r, err := srv.Users.Messages.List(user).Q("is:unread").Do()
		if err != nil {
			log.Fatalf("Unable to retrieve messages: %v", err)
		}
		if len(r.Messages) == 0 {
			fmt.Println("No Messages found.")
		}
		for _, l := range r.Messages {
			m, err := srv.Users.Messages.Get(user, l.ThreadId).Format("full").Do()
			if err != nil {
				fmt.Print("borked")
			}

			frommail := ""
			for _, v := range m.Payload.Headers {
				if v.Name == "From" {
					frommail = v.Value

				}
			}

			if err != nil {
				fmt.Printf("modify broke %v ", err)
			}

			for _, part := range m.Payload.Parts {

				if part.MimeType == "text/html" {

					data, _ := base64.URLEncoding.DecodeString(part.Body.Data)
					html := string(data)
					if checkemail(html) {
						sendmail(*srv, frommail, m.Id, user)
						fmt.Printf("sent email to %s\n", frommail)
					} else {
						sendwrongmail(*srv, frommail, m.Id, user)
					}
				}
			}

		}
		time.Sleep(55 * time.Second)
	}
}
