'use strict'

const express = require('express')
const bodyParser = require('body-parser')
const request = require('request')

const v_token = process.env.FB_VERIFY_TOKEN
const a_token = process.env.FB_ACCESS_TOKEN

const app = express()

app.set('port', (process.env.PORT || 5000))

//allows us to process the data
app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())

//ROUTES

app.get('/', function(req, res) {
  res.send("Hola, estoy aqui para ayudarte")
})

//Facebook

app.get('/webhook/', function(req, res) {
  if (req.query['hub.verify_token'] === v_token) {
    res.send(req.query['hub.challenge'])
  }
  res.send("Wrong Token")
})

app.post('/webhook/', function(req, res) {
  let messaging_events = req.body.entry[0].messaging
  for (let i = 0; i < messaging_events.length; i++) {
    let event = messaging_events[i]
    let sender = event.sender.id
    if (event.message && event.message.text) {
      let text = event.message.text
      decideMessage(sender, text)
    }
    if (event.postback) {
      let text = JSON.stringify(event.postback)
      decideMessage(sender, text)

    }
  }
  res.sendStatus(200)
})

function decideMessage(sender, text1) {
  let text = text1.toLowerCase()
  if (text.includes("start")) {
    sendButtonMessage(sender, "¿Que quieres hacer?", [["Empezar a chatear", "chatear"], ["Ir a la pagina web", "web"]])
  } else if(text.includes("chatear")) {
    sendImageMessage(sender, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkgQAxIYGfodDctizYg_auYhrJO4Jlcy1tGQbvNy9Brp-ZIpNXNQ")

  } else {
    sendText(sender, "Disculpa, no entiendo lo que dices")
  }
}

function sendButtonMessage(sender, text) {
  let messageData = {
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text": text,
        "buttons":[
          {
            "type":"postback",
            "title":"Empezar a chatear",
            "payload":"chatear"
          },
          {
            "type":"postback",
            "title":"Ir a la pagina web",
            "payload":"web"
          }
        ]
      }
    }
  }
  sendRequest(sender, messageData)
}

function sendImageMessage(sender, imageURL) {
  let messageData = {
    "attachment":{
      "type":"image",
      "payload":{
        "url":imageURL
      }
    }
  }
  sendRequest(sender, messageData)
}

function sendText(sender, text) {
  let messageData = {"text": text}
  sendRequest(sender, messageData)
}

function sendRequest(sender, messageData) {
  request({
    url: "https://graph.facebook.com/v2.6/me/messages",
    qs: {access_token: a_token},
    method: "POST",
    json: {
      recipient: {id: sender},
      message: messageData,
    }
  }, function(error, response, body){
    if (error) {
      console.log("sending error")
    } else if (response.body.error) {
      console.log("response body error")
    }
  })
}

app.listen(app.get('port'), function() {
  console.log("Estoy corriendo: port")
})
