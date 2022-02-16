<template>
	<div class="col-sm col-md col-lg-6">
		<canvas class="canvas" v-bind:id="'chart-' + examId"></canvas>
	</div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
	name: "ChartComponent",
	props: {
		examId: Number,
	},
	methods: {
		getCharts() {
			axios
				.get(`${this.path}`)
				.then((res) => {
					if (!res.data.grades || !res.data.dates) {
						return;
					}

					const chart = document.getElementById(`chart-${this.examId}`);
					const ctx = chart.getContext("2d");
					const gradient = ctx.createLinearGradient(0, 0, 0, 300);

					gradient.addColorStop(0, "rgba(99, 108, 179, 1)");
					gradient.addColorStop(1, "rgba(99, 108, 179, 0)");
					new Chart(ctx, {
						type: "line",
						data: {
							labels: res.data.dates,
							datasets: [
								{
									label: `${res.data.exam_name}`,
									data: res.data.grades,
									backgroundColor: gradient,
									fill: true,
									strokeColor: "#636cb3",
								},
							],
						},
						options: {
							elements: {
								line: {
									tension: 0.4, // disables bezier curves
								},
							},
							scales: {
								x: {
									ticks: {
										autoSkip: true,
										maxRotation: 0,
										padding: 3,
									},
								},
							},
						},
					});
				})
				.catch((error) => {
					console.error(error);
				});
		},
	},
	computed: {
		path() {
			return `/api/progress/${this.examId}`;
		},
	},
	created() {
		this.getCharts();
	},
};
</script>
