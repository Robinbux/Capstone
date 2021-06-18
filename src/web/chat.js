// Startup functions
$( document ).ready(function() {
    setUUID();
    setName();
    loadChatOverview();
    loadChatHistory();
});

async function setUUID() {
    let uuid = await eel.get_uuid()();
    console.log("SET UUID: " + uuid)
    $("#uuid-text").text(uuid);
}

async function setName() {
    let name = await eel.get_name()();
    console.log("SET Name: " + name)
    $("#name-text").text(name);
}

async function loadChatOverview() {
    let chatOverview = await eel.load_chat_overview()();
    console.log("Chat overview: " + chatOverview)
    let chatOverviewJSON = JSON.parse(chatOverview)

    chatOverviewJSON.forEach(contact => {
        addChat(contact.name, contact.uuid)
    });
}

async function loadChatHistory() {
    let chatHistory = await eel.load_chat_history()();
    console.log("Chat history: " + chatHistory)
    let chatHistoryJSON = JSON.parse(chatHistory)
    chatHistoryJSON.sort(compareHistory)
    console.log(chatHistoryJSON)

    chatHistoryJSON.forEach(history => {
        console.log("IN HISTORY!")
        // Get imessage with correct id
        let idStr = "msg-" + history.contact
        let imessage = $("#"+idStr)
        console.log(imessage)

        // If message doesn't exsist, create one
        if (!imessage) {
            imessage = document.createElement("div");
            imessage.classList.add('imessage')
            imessage.id = idStr
            fullChat.prepend(imessage)
        }
        let senderClass = history.sentBy == "ME" ? "from-me" : "from-them";

        let chatMessage = document.createElement("p");
        chatMessage.classList.add(senderClass, 'no-tail')
        chatMessage.id = idStr
        chatMessage.innerHTML = history.message

        imessage.append(chatMessage)
    });
}

// Sort by date
function compareHistory(messageOne, messageTwo) {
    if (messageOne.date > messageTwo.date) return 1;
    return -1;
}

// Add Contact Modal Button
$('.ui.basic.button').click(function() {
    $('.ui.modal').modal('show');
});

// Add Contact Button
$('.add-contact').click(function() {
    let successMessage = $('#add-contact-success')
    let failureMessage = $('#add-contact-failure')

    let uuid = $('#add-contact-uuid').val()
    console.log("UUID: " + uuid)

    //successMessage.removeClass('hidden')
    result = eel.contact_connection_request(uuid);
    console.log("Result: " + result)
});

// Copy Button
function copyToClipboard(element) {
    let $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}

// Add a new chat
function addChat(contactName, contactUUID) {
    console.log("ADDING NEW CHAT")
    console.log("Contact name: " + contactName)
    console.log("Contact UUID: " + contactUUID)

    let profileImage = document.createElement("img");
    profileImage.classList.add('ui', 'avatar', 'image');
    profileImage.src = "https://semantic-ui.com/images/avatar/large/stevie.jpg"

    let header = document.createElement("div");
    header.classList.add('header')
    header.innerHTML= contactName

    let description = document.createElement("div");
    description.classList.add('description')
    description.innerHTML=contactUUID

    let content = document.createElement("div");
    content.classList.add('content')
    content.appendChild(header)
    content.appendChild(description)

    let lastSeenDescription = document.createElement("div");
    lastSeenDescription.classList.add('description')

    let rightFloatedContent = document.createElement("div");
    rightFloatedContent.classList.add('right', 'floated', 'content')
    rightFloatedContent.appendChild(lastSeenDescription)

    let chatItem = document.createElement("div");
    chatItem.classList.add('item');


    //chatItem.onclick = setChatActive(this)
    chatItem.setAttribute("onclick", "setChatActive(this)");

    chatItem.appendChild(profileImage)
    chatItem.appendChild(content)
    chatItem.appendChild(rightFloatedContent)
    chatItem.id = contactUUID

    chatOverview.appendChild(chatItem)

    // Add full message
    let imessage = document.createElement("div");
    imessage.classList.add('imessage')
    imessage.id = "msg-" + contactUUID

    fullChat.prepend(imessage)

    return imessage
}

// Handle add contact
eel.expose(handleAddContactResponse);
function handleAddContactResponse(response_json_str) {
    let successMessage = $('#add-contact-success')
    let failureMessage = $('#add-contact-failure')
    console.log("*******************************")
    console.log("Handle Add Contact Response")
    console.log("*******************************")
    console.log(response_json_str)
    // Javascript only recognizes lower-case True and False
    response_json_str = response_json_str.replace("True", "true").replace("False",
        "false")
    console.log(response_json_str)
    response_json = JSON.parse(response_json_str)
    console.log(response_json)
    if (response_json.contactExists) {
        console.log("Contact Exists!")
        successMessage.removeClass('hidden')
        // Add to contact list
        addChat(response_json.contactName, response_json.contactUUID)

    } else {
        failureMessage.removeClass('hidden')
    }
}

console.log("START")

list = $('.ui.list')

let chatOverview = document.getElementById("chat-overview");
let chatPreviews = document.querySelectorAll('.chat-overview .item')
let fullChat = document.getElementById("full-chat")
let fullChats = document.querySelectorAll('.imessage')

let activePreview

function setChatActive(chatPreviewItem) {
    console.log("SET CHAT ACTIVE")
    console.log(chatPreviewItem)
    let chatPreviews = document.querySelectorAll('.chat-overview .item')
    let fullChats = document.querySelectorAll('.imessage')
    // Remove old active
    Array.from(chatPreviews).forEach(chatPreview => chatPreview.classList.remove('active'))
    Array.from(fullChats).forEach(fullChat => fullChat.classList.remove('active'))

    // Get new chat to activate
    let fullChatId = "msg-" + chatPreviewItem.id

    // Set actives
    activePreview = chatPreviewItem
    activeChat = Array.from(fullChats).find((node) => node.id === fullChatId)

    // Set new
    activePreview.classList.add('active')
    activeChat.classList.add('active');
}

let chatInput = $(".chat-input")
// Send message
chatInput.on('keyup', function (e) {
    if (e.key === 'Enter' || e.keyCode === 13) {
        // Get Message
        let message = chatInput.val()

        // Clean field
        chatInput.val('')

        // Add to chat
        let messageEl = document.createElement("p");
        messageEl.classList.add('from-me', 'no-tail');
        messageEl.innerHTML = message;
        activeChat.appendChild(messageEl)

        eel.send_message(activePreview.id, message);

    }
});

eel.expose(handleIncomingMessage);
function handleIncomingMessage(messageJsonStr) {
    fullChats = document.querySelectorAll('.imessage')
    messageJSON = JSON.parse(messageJsonStr)

    console.log(messageJSON)

    let fullChatId = "msg-" + messageJSON.senderUUID
    senderChat = Array.from(fullChats).find((node) => node.id === fullChatId)

    console.log(senderChat)

    if (!senderChat) {
        console.log("New contact!")
        // Add chat
        senderChat = addChat(messageJSON.senderName, messageJSON.senderUUID)
        console.log("After Add chat!")
        console.log(senderChat)
    }


    let messageEl = document.createElement("p");
    messageEl.classList.add('from-them', 'no-tail');
    messageEl.innerHTML = messageJSON.message;

    senderChat.appendChild(messageEl)
}
