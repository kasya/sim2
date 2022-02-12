<template>
	<div class="container-fluid">
		<h2>Please choose the subject of your exam:</h2>
		<select
			class="form-select"
			name="subjects"
			id="subjects"
			v-model="selected"
			v-on:change="getExams"
		>
			<option v-bind:key="s.id" v-bind:value="s.id" v-for="s in subjects">
				{{ s.name }}
			</option>
		</select>
		<div v-show="exams.length > 0">
			<p>Please choose the exam you want to take:</p>
			<select
				class="form-select"
				name="exams"
				id="exams"
				v-model="exam_selected"
			>
				<option v-bind:key="e.id" v-bind:value="e.id" v-for="e in exams">
					{{ e.name }}
				</option>
			</select>
		</div>
		<button
			class="btn bg-gradient-info w-auto me-1 mb-0"
			type="button"
			v-on:click="startExam"
			v-show="exam_selected != -1"
		>
			Select
		</button>
	</div>
</template>

<script>
import axios from "axios";

export default {
	name: "SubjectComponent",
	data() {
		return {
			subjects: {},
			exams: {},
			selected: -1,
			exam_selected: -1,
		};
	},
	methods: {
		getSubjects() {
			axios
				.get(this.path)
				.then((res) => {
					this.subjects = res.data;
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
				});
		},
		getExams() {
			axios
				.get(`/api/subject/${this.selected}/exams/`)
				.then((res) => {
					this.exams = res.data;
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
				});
		},
		startExam() {
			window.location.href = "/exam/" + this.exam_selected + "/intro/";
		},
	},
	computed: {
		path() {
			return "/api/subject/";
		},
	},
	created() {
		this.getSubjects();
	},
};
</script>
