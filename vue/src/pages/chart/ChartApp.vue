<template>
	<div class="row">
		<chart v-for="examId in examIds" :exam-id="examId" :key="examId" />
	</div>
</template>

<script>
import Chart from "../../components/Chart.vue";

export default {
	props: {
		examId: String,
	},
	components: {
		Chart,
	},
	data() {
		return {
			examIds: [],
		};
	},
	mounted() {
		let examIds = this.examId;
		examIds = examIds.slice(1, examIds.length - 1);

		this.examIds = examIds.split(",").map(Number);
	},
};
</script>
