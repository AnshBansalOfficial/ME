// Define the activation states (0 for locked, 1 for active)
const cardStates = {
    augSep: 1, // Change this to 0 to lock the card
    octNov: 0, // Change this to 1 to activate the card
    decMarch: 0, // Change this to 1 to activate the card
    aprJun: 0  // Change this to 1 to activate the card
  };
  
  // Function to apply styles based on card state
  function applyCardStates() {
    Object.keys(cardStates).forEach(cardId => {
      const card = document.getElementById(cardId);
      const isActive = cardStates[cardId] === 1;
  
      if (isActive) {
        // Card is active
        card.classList.remove('locked');
        card.querySelector('.btn-primary').classList.remove('locked');
        card.querySelector('.card-title').classList.remove('locked');
      } else {
        // Card is locked
        card.classList.add('locked');
        card.querySelector('.btn-primary').classList.add('locked');
        card.querySelector('.card-title').classList.add('locked');
      }
    });
  }
  
  // Run the function on page load
  window.onload = applyCardStates;
  