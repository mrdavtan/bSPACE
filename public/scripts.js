async function loadMostRecentJson() {
  try {
    const response = await fetch('http://localhost:3002/api/latest-json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Most recent JSON:', data);
    // Use the data as needed in your client-side app
  } catch (error) {
    console.error('Could not load the most recent JSON file:', error);
    // Handle the error, e.g., display an error message to the user
    alert('Failed to load the most recent JSON file. Please try again later.');
  }
}

loadMostRecentJson();
