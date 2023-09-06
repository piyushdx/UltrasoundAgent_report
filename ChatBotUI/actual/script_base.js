const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const BOT_MSGS = [
  "Hi, how are you?",
  "Ohh... I can't understand what you trying to say. Sorry!",
  "I like to play games... But I don't know how to play!",
  "Sorry if my answers are not relevant. :))",
  "I feel sleepy! :(",
];

// Icons made by Freepik from www.flaticon.com
const BOT_IMG = "static/images/bot.ico";
const PERSON_IMG = "static/images/user3.png";
const BOT_NAME = "ALEX";
const PERSON_NAME = "User";
// const workout_type : droupdown
// const equipment  : dropdown
// const fitness_level : dropdown
// const body_focus : dropdown
// const days : dropdown [1, 7]
// const time : input (numbers) Dropdown (hour / min)
// 								[1-5]   [0-999]



const currentURL = window.location.href;
const urlParts = currentURL.split('/'); // Split the URL by '/'
const lastWord = urlParts[urlParts.length - 1]; // Get the last element
// var url = ""
// var cache_value = ""
const base_url = "http://127.0.0.1:1563/"
const url_dictionary = {
  "get_response": {"FitnessBot":"Fitness_get_response",
  "MembershipBot":"Membership_get_response",
  "InternetSearch":"InternetSearch_get_response",
  "UltraBot":"UltraBot_get_response",},

  "clear_cache": {"FitnessBot":"Fitness_clear_cache",
  "MembershipBot":"Membership_clear_cache",
  "InternetSearch": "InternetSearch_clear_cache",
  "UltraBot": "UltraBot_clear_cache",}}
var value = url_dictionary['get_response'][lastWord];
var modifiedURL = base_url + value;

var cache_value = url_dictionary['clear_cache'][lastWord];
var cachemodifiedURL = base_url + cache_value;

console.log('modifiedURL:',modifiedURL)
console.log('cachemodifiedURL:',cachemodifiedURL)



msgerForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const msgText = msgerInput.value;
  if (!msgText) return;

  appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
  msgerInput.value = "";

  // FIX-ME: change this payload data
  let requestPayload = { query: msgText, type: "" };
  let response = await sendMessageApiCall(requestPayload);
});

// http://127.0.0.1:5000
// 18.144.92.141:8503

function sendMessageApiCall(data) {
  // Show the loader icon
  appendLoader(BOT_NAME, BOT_IMG, "left", "<div id='loading-icon' class='loader'><span></span><span></span><span></span></div>")
  const loader = document.getElementById('loading-icon');
  loader.style.display = 'block';
  // Disable the button
  disableAndFreezeButton("SendBtnID")

  // FIX-ME: change this api call
  console.log(data);
  
  // fetch("http://127.0.0.1:1563/get_response", {
    fetch(modifiedURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      let response1 = response.json();

      return response1;
    })
    .then((data) => {
      botResponse(data);
      console.log("Success here:", data);
      // Once the response is received, hide the loader icon
      loader.style.display = 'none';
      const loaderCLS = document.getElementById('loaderID');
      loaderCLS.remove();
      // Enable the button
      enableAndUnfreezeButton("SendBtnID")
    })
    .catch((error) => {
      console.error("Error:", error);
    });


}


function convertPdf() {
  const form = document.getElementById("upload-form");
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission
    
    const formData = new FormData(form);
    alert("PDF uploaded successfully!");
    fetch(base_url+"convert", {
      method: "POST",
  
      body: formData,
    })

    // fetch("http://192.168.2.69:8001/convert", {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //   },
    //   body: JSON.stringify(formData),
    // })

      .then(response => {
        // Handle response if needed
        if (response.ok) {
          return response.json(); // Parse response as JSON
        }
        throw new Error("Network response was not ok.");
      })
      .then((formData) => {
        botResponse(formData);
        console.log("Success here:", formData);
        // Once the response is received, hide the loader icon
        loader.style.display = 'none';
        const loaderCLS = document.getElementById('loaderID');
        loaderCLS.remove();
        // Enable the button
        enableAndUnfreezeButton("SendBtnID")
      })
      // .then(data => {
      //   const responseDiv = document.getElementById("response");
      //   responseDiv.innerHTML = `Response from server: ${data.message}`;
      // })
      .catch(error => {
        console.error("Error:", error);
      });
  });
}

document.addEventListener("DOMContentLoaded", convertPdf);





// Disable and freeze the button
function disableAndFreezeButton(buttonId) {
  var button = document.getElementById(buttonId);
  button.disabled = true;
  button.classList.add("freeze");
}

// Enable and unfreeze the button
function enableAndUnfreezeButton(buttonId) {
  var button = document.getElementById(buttonId);
  button.disabled = false;
  button.classList.remove("freeze");
}



function appendLoader(name, img, side, text) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg" id='loaderID'>
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}


function appendMessage(name, img, side, texts) {
  // Convert texts to an array if it's a single string
  if (!Array.isArray(texts)) {
    texts = [texts];
  }

  // Iterate over the array of texts
  texts.forEach(function(text) {
    if (text.trim() === "") {
      return;
    }
    const msgHTML = `
      <div class="msg ${side}-msg">
        <div class="msg-img" style="background-image: url(${img})"></div>
  
        <div class="msg-bubble">
          <div class="msg-info">
            <div class="msg-info-name">${name}</div>
            <div class="msg-info-time">${formatDate(new Date())}</div>
          </div>
  
          <div class="msg-text">${text}</div>
        </div>
      </div>
    `;
  
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  });

  // Scroll to the bottom of the chat
  msgerChat.scrollTop = msgerChat.scrollHeight;
}

function appendFormMessage(name, img, side) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">
        <form onsubmit="postData()">
          <div class="form-div">
          <label>
            workout_type :
            <select name="type" id="type">
                <option value="cardio">cardio</option>
                </option>
                <option value="yoga">yoga</option>
                <option value="pilates">pilates</option>
                <option value="hiit">hiit</option>
                <option value="strength">strength</option>
                <option value="mobility">mobility</option>
                <option value="low_impact">low_impact</option>
                <option value="ride">ride</option>
                <option value="dance">dance</option>
                <option value="tips_and_tricks">tips_and_tricks</option>
                <option value="get_personal">get_personal</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <label>
            equipment :
            <select name="equipment" id="equipment">
                <option value="hand_weights">hand_weights</option>
                <option value="kettlebell">kettlebell</option>
                <option value="bike">bike</option>
                <option value="resistance_bands">resistance_bands</option>
                <option value="chair">chair</option>
                <option value="hula_hoop">hula_hoop</option>
                <option value="no_equipment_needed">no_equipment_needed</option>
                <option value="body_bar">body_bar</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <label>
            fitness_level :
            <select name="level" id="level">
                <option value="im_new_here">im_new_here</option>
                <option value="some_days_off">some_days_off</option>
                <option value="beast_mode">beast_mode</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <label>
            body_focus :
            <select name="body_focus" id="body_focus">
                <option value="lower_body">lower_body</option>
                <option value="full_body">full_body</option>
                <option value="upper_body">upper_body</option>
                <option value="booty">booty</option>
                <option value="abs">abs</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <label>
            days :
            <select name="days" id="days">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5"selected>5</option>
                <option value="6">6</option>
                <option value="7">7</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <label>
            time :
            <input type="number" name="time" id="time" value="30">
            <select name="format" id="format">
                <option value="min">Min</option>
                <option value="hr">Hour</option>
            </select>
          </label>
      </div>
      <div class="form-div">
          <div style="float:right;margin: 5px 0px;width: 20%">
            <button class="msger-send-btn" id="form-submit" type="submit">Send</button>
          </div>
      </div>
      </form>
      </div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

const handleFormSubmit = () => {
   let workout_type = get("#type").value;
   let equipment = get("#equipment").value;
   let level = get("#level").value;
   let body_focus = get("#body_focus").value;
   let days = parseInt(get("#days").value);
   let time = get("#time").value.concat(" ", get("#format").value);
   let type = "Form";

   const formData = {
        workout_type,
        equipment,
        level,
        body_focus,
        days,
        time,
   }

    console.log(formData)

    // fetch("http://127.0.0.1:1563/get_response", {
    fetch(modifiedURL,{
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({query : formData, type: type}),

  })
    .then((response) => {
      let response1 = response.json();

      return response1;
    })
    .then((data) => {
      botResponse(data);
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });

};



function nl2br(input, is_xhtml) {
  var breakTag =
    is_xhtml || typeof is_xhtml === "undefined" ? "<br />" : "<br>";

  // Check if the input is an array
  if (Array.isArray(input)) {
    // Apply the line break conversion to each element in the array
    return input.map(function(str) {
      return (str + "").replace(
        /([^>\r\n]?)(\r\n|\n\r|\r|\n)/g,
        "$1" + breakTag + "$2"
      );
    });
  } else {
    // If the input is not an array, apply the line break conversion to the string
    return (input + "").replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, "$1" + breakTag + "$2");
  }
}


function makeUrlsClickable(messages) {
  if (!Array.isArray(messages)) {
    return messages;
  }

  const urlRegex = /(https?:\/\/?\S+)/g;

  return messages.map((message) => {
    if (typeof message !== "string") {
      return message;
    }

    return message.replace(urlRegex, (url) => {
      const href = url.trim();
      return `<a href="${href}" target="_blank">${url}</a>`;
    });
  });
}



function botResponse(requestPayload) {
  let msgText = requestPayload.response;
//   if (
//     msgText ===
//       "sure i can help you with that. before that can you answer few questions."
// //    msgText ===
// //      "Hi can you tell me what equipment type do you have to do workout?"
//   ) {
//     appendFormMessage(BOT_NAME, BOT_IMG, "left");
//     const gymForm = get("#form-submit");
//     gymForm.onclick = function (e) {
//       e.preventDefault();
//       handleFormSubmit();
//     };
//   } else {
    
    msgText = nl2br(msgText);
    msgText = makeUrlsClickable(msgText);
    console.log(msgText);
    const delay = 0;
    setTimeout(() => {
      appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
    }, delay);
  }
// }

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}

function openPopup() {
  var popup = document.getElementById("myPopup");
  popup.style.display = "block";
  setTimeout(function() {
    document.addEventListener("click", closePopupOutside);
  }, 0);
}

function closePopup() {
  var popup = document.getElementById("myPopup");
  popup.style.display = "none";
  document.removeEventListener("click", closePopupOutside);
}

function closePopupOutside(event) {
  var popup = document.getElementById("myPopup");
  var target = event.target;
  
  // Check if the target element is inside the popup
  if (target !== popup && !popup.contains(target)) {
    closePopup();
  }
}


var clearChatButton = document.getElementById("clearChatButton");

// Add click event listener to the button
clearChatButton.addEventListener("click", function() {
  // Clear the chat or perform any desired action
  
  deleteChatData();
  // Refresh the page
  location.reload();
});


// Function to delete chat data using an API
function deleteChatData() {
  // Perform the necessary steps to call the API and delete the chat data
  // You can use libraries like fetch, axios, or jQuery.ajax to make the API request

  // Example using fetch:
  fetch(cachemodifiedURL, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    // Include any necessary authentication or request payload
    // body: JSON.stringify({}),
  })
    .then(response => {
      // Handle the API response as needed
      if (response.ok) {
        console.log("Chat data deleted successfully.");
      } else {
        console.error("Failed to delete chat data.");
      }
    })
    .catch(error => {
      console.error("An error occurred while deleting chat data:", error);
    });
}