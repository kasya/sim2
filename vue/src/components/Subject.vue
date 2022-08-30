<template>
	<div class="container-fluid">
		<h2>Let's get started.</h2>
		<h4>Please choose the subject of your exam:</h4>
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
			<h4>Now choose what would you like to do:</h4>
			<input
				type="radio"
				id="subject_exam"
				name="subject_or_category"
				value="subject_exam"
				v-model="exam_type"
			/><label for="subject_exam">
				Take en exam on whole subject (covers all categories from chosen
				subject) </label
			><br />
			<input
				type="radio"
				id="category_exam"
				name="subject_or_category"
				value="category_exam"
				v-model="exam_type"
			/><label for="category_exam"
				>Choose one category to take an exam on.</label
			><br />
			<h4 v-show="exam_type == 'category_exam'">
				Now choose the exam category:
			</h4>
			<select
				class="form-select"
				name="exams"
				id="exams"
				v-model="exam_selected"
				v-show="exam_type == 'category_exam'"
			>
				<option v-bind:key="e.id" v-bind:value="e.id" v-for="e in exams">
					{{ e.name }}
				</option>
			</select>
		</div>
		<div v-show="exam_type.length > 0">
			<h4>Pick exam or practice mode:</h4>
			<input
				type="radio"
				id="practice_mode"
				name="mode"
				value="practice"
				v-model="picked"
			/><label for="practice_mode"
				><p>Practice mode (you will see correct answers right away)</p></label
			><br />
			<input
				type="radio"
				id="exam_mode"
				name="mode"
				value="exam"
				v-model="picked"
			/><label for="exam_mode"
				><p>Exam mode (your answers will be graded at the end)</p></label
			><br />
		</div>
		<button
			class="btn bg-gradient-info w-auto me-1 mb-0"
			type="button"
			v-on:click="startExam"
			v-show="picked.length > 0"
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
			picked: "",
			exam_type: "",
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
			if (this.exam_selected > 0) {
				window.location.href = `/exam/${this.exam_selected}/${this.picked}/intro/`;
			} else {
				window.location.href = `/exam/subject/${this.selected}/${this.picked}/intro/`;
			}
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
