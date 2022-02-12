import axios from "axios";
import { createApp } from "vue";

import App from "./ExamApp.vue";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

const rootElementId = "#exam";
const rootElement = document.querySelector(rootElementId);

const app = createApp(App, { ...rootElement.dataset });
app.mount(rootElementId);
