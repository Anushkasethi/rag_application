import React from 'react';
import ReactDOM from 'react-dom';
// import './index.css';  // Optional: If you have global styles
import App from './App';  // Import your main App component
// import reportWebVitals from './reportWebVitals'; // Optional: For measuring performance (if you need)

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root') // This links to the <div id="root"></div> in index.html
);

// Optional: For measuring performance
// reportWebVitals();
