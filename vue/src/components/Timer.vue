<template>
	<div class="progress">
		<div
			class="progress-bar progress-bar-striped bg-info"
			id="progress_bar"
			role="progressbar"
			aria-valuemin="0"
			aria-valuemax="100"
		></div>
	</div>
</template>

<script>
import axios from "axios";

export default {
	name: "TimerComponent",
	props: {
		attemptId: String,
	},
	data() {
		return {
			attempt: {},
		};
	},
	methods: {
		getAttempt() {
			axios
				.get(this.attemptPath)
				.then((res) => {
					this.attempt = res.data;
					let that = this;
					const counterBack = setInterval(function () {
						let percent = parseInt(
							(that.attempt.time_left_seconds * 100) /
								(that.attempt.attempt_duration_minutes * 60)
						);
						if (percent >= 0) {
							document.getElementById("progress_bar").style.width =
								percent + "%";
							document.getElementById("progress_bar").innerHTML =
								Math.floor(that.attempt.time_left_seconds / 60)
									.toString()
									.padStart(2, "0") +
								":" +
								(that.attempt.time_left_seconds % 60)
									.toString()
									.padStart(2, "0");

							that.attempt.time_left_seconds--;
						} else {
							clearInterval(counterBack);
							window.location.href = `/exam/${that.attemptId}/finish`;
						}
					}, 1000);
				})
				.catch((error) => {
					// eslint-disable-next-line
					this.error = error.response.data.message;
					console.error(error.response);
				});
		},
	},
	computed: {
		attemptPath() {
			return `/api/attempt/${this.attemptId}`;
		},
	},
	created() {
		this.getAttempt();
	},
};
</script>
