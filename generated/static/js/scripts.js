document.addEventListener("DOMContentLoaded", () => {
  const playButton = document.getElementById("play_button");
  const newCampaignButton = document.getElementById("new_campaign_button");
  const submitCampaign = document.getElementById("submit_campaign");
  const addCharacterButton = document.getElementById("add_character_button");
  const continueCharacters = document.getElementById("continue_characters");
  const rollCharacterButton = document.getElementById("roll_character_button");
  const continueCharacterCreation = document.getElementById("continue_character_creation");
  const chatInput = document.getElementById("chat_input");

  playButton.addEventListener("click", () => {
    window.location.href = "/game";
  });

  newCampaignButton.addEventListener("click", () => {
    window.location.href = "/new_campaign";
  });

  submitCampaign.addEventListener("click", () => {
    const campaignDescription = document.getElementById("campaign_description").value;
    if (campaignDescription.trim() !== "") {
      window.location.href = `/character_list?description=${encodeURIComponent(campaignDescription)}`;
    }
  });

  addCharacterButton.addEventListener("click", () => {
    window.location.href = "/character_creation";
  });

  continueCharacters.addEventListener("click", () => {
    window.location.href = "/play";
  });

  rollCharacterButton.addEventListener("click", async () => {
    const response = await fetch("/api/roll_character");
    const characterData = await response.json();
    document.getElementById("character_role").innerText = characterData.role;
    document.getElementById("character_type").innerText = characterData.type;
    document.getElementById("character_backstory").value = characterData.backstory;
    document.getElementById("character_attributes").innerText = characterData.attributes.join(", ");
    document.getElementById("character_primary_goal").value = characterData.primary_goal;
    document.getElementById("character_inventory").innerText = characterData.inventory.join(", ");
  });

  continueCharacterCreation.addEventListener("click", () => {
    window.location.href = "/character_list";
  });

  chatInput.addEventListener("keydown", async (event) => {
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