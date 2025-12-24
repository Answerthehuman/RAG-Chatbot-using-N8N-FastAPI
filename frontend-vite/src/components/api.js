import axios from 'axios';

/** @type {import('axios').Axios} */
const api = axios.create({
    baseURL: 'http://localhost:8000'
});

export default api;