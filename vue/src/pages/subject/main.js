import axios from "axios";
import { createApp } from "vue";

import App from "./SubjectApp.vue";

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "x-csrftoken";

createApp(App).mount("#subject");
