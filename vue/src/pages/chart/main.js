import axios from "axios";
import { createApp } from "vue";

import App from "./ChartApp.vue";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

const rootElementId = "#chart";
const rootElement = document.querySelector(rootElementId);

createApp(App, { ...rootElement.dataset }).mount(rootElementId);
