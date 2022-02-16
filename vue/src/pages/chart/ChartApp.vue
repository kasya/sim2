<template>
	<div class="row">
		<chart v-for="examId in examIdList" :exam-id="examId" :key="examId" />
	</div>
</template>

<script>
import Chart from "../../components/Chart.vue";

export default {
	props: {
		examIds: String,
	},
	components: {
		Chart,
	},
	data() {
		return {
			examIdList: [],
		};
	},
	mounted() {
		let examIdList = this.examIds;
		this.examIdList = examIdList
			.slice(1, examIdList.length - 1)
			.split(",")
			.map(Number);
	},
};
</script>
