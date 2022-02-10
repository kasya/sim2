const app = Vue.createApp({
	data() {
		return {
			subject: "English",
		};
	},
});

app.config.compilerOptions.delimiters = ["{(", ")}"];
