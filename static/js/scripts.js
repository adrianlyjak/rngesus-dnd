document.addEventListener("DOMContentLoaded", () => {
  const playButton = document.getElementById("play_button");
  const newCampaignButton = document.getElementById("new_campaign_button");
  const submitCampaign = document.getElementById("submit_campaign");
  const addCharacterButton = document.getElementById("add_character_button");
  const continueCharacters = document.getElementById("continue_characters");
  const rollCharacterButton = document.getElementById("roll_character_button");
  const chatInput = document.getElementById("chat_input");

  playButton?.addEventListener("click", () => {
    window.location.href = "/game";
  });

  newCampaignButton?.addEventListener("click", () => {
    window.location.href = "/new_campaign";
  });

  submitCampaign?.addEventListener("click", () => {
    const campaignDescription = document.getElementById("campaign_description").value;
    if (campaignDescription.trim() !== "") {
      window.location.href = `/character_list?description=${encodeURIComponent(campaignDescription)}`;
    }
  });

  addCharacterButton?.addEventListener("click", () => {
    let paths = window.location.pathname.split("/")
    let path = paths[paths.length - 1];
    window.location.href = "/character_creation/" + path;
  });

  continueCharacters?.addEventListener("click", () => {
    window.location.href = "/play";
  });


  rollCharacterButton?.addEventListener("click", async () => {
    let paths = window.location.pathname.split("/")
    let path = paths[paths.length - 1];
    const response = await fetch("/api/roll_character/" + encodeURIComponent(path));
    const characterData = await response.json();
    let characterContainer = document.getElementById("character");
    characterContainer.innerText = JSON.stringify(characterData, null, 2);
    let hidden = document.getElementById("characterHidden");
    hidden.value = JSON.stringify(characterData);
  });

  
  chatInput?.addEventListener("keydown", async (event) => {
    if (event.key === "Enter") {
      const message = chatInput.value.trim();
      if (message !== "") {
        const response = await fetch("/api/send_message", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ message })
        });
        const chatMessage = await response.json();
        const chatHistory = document.getElementById("chat_history");
        const newMessage = document.createElement("div");
        newMessage.innerText = chatMessage.message;
        chatHistory.appendChild(newMessage);
        chatInput.value = "";
      }
    }
  });
});