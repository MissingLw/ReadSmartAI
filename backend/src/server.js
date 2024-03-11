const express = require('express');
const app = express();
const axios = require('axios');
const path = require('path');
const session = require('express-session');

app.use(express.json());
app.use(express.static(path.join(__dirname, '../../frontend/src'))); // Serve static files
app.set('views', path.join(__dirname, '../../frontend/src/views')); // Set views directory
app.set('view engine', 'ejs');

app.use(session({
  secret: 'your secret',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Note: secure should be set to true when in production
}));

// Route for root URL
app.get('/', (req, res) => {
    res.redirect('/question');
});

// Route for question creation screen
app.get('/question', (req, res) => {
    res.render('question');
});

app.post('/question', async (req, res) => {
    console.log('Received POST request at /question with body:', req.body);
    // Send a request to the question_generator.py microservice
    const questions = await axios.post('http://localhost:5000/generate', req.body);
    console.log('Received questions from question_generator.py:', questions.data);
    req.session.qa_pairs = questions.data; // Save the questions in the session
    res.redirect('/answer');
});

// Route for answer screen
app.get('/answer', (req, res) => {
    console.log('Received GET request at /answer');
    res.render('answer', { qa_pairs: req.session.qa_pairs }); // Pass the questions to the answer.ejs file
});

// New route handler for /qa_pairs
app.get('/qa_pairs', (req, res) => {
    console.log('Received GET request at /qa_pairs');
    res.json(req.session.qa_pairs);
});

app.post('/answer', async (req, res) => {
    console.log('Received POST request at /answer with body:', req.body);
    // Send a request to the response_grader.py microservice
    try {
        const feedback = await axios.post('http://localhost:5001/grade', {
            qa_pairs: req.session.qa_pairs,
            student_responses: req.body.answers.reduce((obj, answer, i) => {
                obj[`Question ${i + 1}`] = answer;
                return obj;
            }, {}),
        });
        console.log('Received feedback from response_grader.py:', feedback.data);
        // Return the feedback as a JSON object
        res.json({ feedback: feedback.data.feedback });
    } catch (error) {
        console.error('Error sending request to response_grader.py:', error.message);
        res.status(500).send('An error occurred while grading the answers.');
    }
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));