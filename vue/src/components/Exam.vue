<template>
	<div>
		<div v-if="error">{{ error }}</div>
		<div>
			<h4>{{ question.text }}</h4>
			<form class="form-check">
				<ul>
					<li v-for="a in question.answers" v-bind:key="a.id">
						<input
							v-if="question.type == 'multiple_choice'"
							class="form-check-input"
							type="radio"
							name="single-answer"
							v-bind:id="a.id"
							v-bind:value="a.id"
							v-model="selected"
						/>

						<input
							v-else
							class="form-check-input"
							type="checkbox"
							name="multiple-answer"
							v-bind:id="a.id"
							v-bind:value="a.id"
							v-model="checked"
						/>
						<label v-bind:for="a.id"></label>
						<p>{{ a.text }}</p>
					</li>
				</ul>
			</form>
			<div>
				<button
					class="btn bg-gradient-info w-auto me-1 mb-0"
					type="button"
					v-on:click="recordAnswer"
					v-show="question.text"
					:disabled="!selected && !checked.length"
				>
					Submit
				</button>

				<nav>
					<ul class="pagination d-flex justify-content-center">
						<li
							class="page-item"
							v-for="i in attempt.question_count"
							v-bind:key="i"
						>
							<a
								class="page-link"
								href="#"
								@click="getQuestion"
								v-bind:id="'q_' + i"
								:data-q-id="answered_questions[i - 1]"
								>{{ i }}</a
							>
						</li>
					</ul>
				</nav>
			</div>
		</div>
	</div>
</template>

<script>
import $ from "jquery";
import axios from "axios";

export default {
	name: "ExamComponent",
	props: {
		attemptId: String,
	},
	data() {
		return {
			answered_questions: [],
			attempt: {},
			checked: [],
			count: 1,
			error: null,
			is_checked: false,
			result: false,
			selected: null,
			question: {},
			question_id: -1,
			multiple_choice: "multiple_choice",
		};
	},
	methods: {
		getNextQuestion() {
			this.is_checked = false;
			this.error = "";
			axios
				.get(this.path)
				.then((res) => {
					if (res.data.id) {
						this.question = res.data;
					} else {
						window.location.href = `/exam/${this.attemptId}/finish`;
					}
				})
				.catch((error) => {
					this.error = error.response.data.message;
					console.error(error.response);
				});
		},
		getQuestion(event) {
			this.question_id = parseInt($(event.target).attr("data-q-id"));
			axios
				.get(`/api/attempt/${this.attemptId}/${this.question_id}`)
				.then((res) => {
					if (res.data["question"]) {
						this.question = res.data["question"];
						if (this.question.type == this.multiple_choice) {
							this.selected = res.data["answer_ids"][0];
						} else {
							this.checked = res.data["answer_ids"];
						}
					} else {
						window.location.href = `/exam/${this.attemptId}/finish`;
					}
				})
				.catch((error) => {
					this.error = error.response.data.message;
					console.error(error.response);
				});
		},
		checkAnswer() {
			axios
				.post(this.path, { answers: this.selected })
				.then((res) => {
					this.result = res.data["is_correct"];
					this.is_checked = true;
				})
				.catch((error) => {
					this.error = error.response.data.message;
					console.error(error.response);
				});
		},
		recordAnswer() {
			this.answer_ids = [];
			if (this.question.type == this.multiple_choice) {
				if (this.selected != null) {
					this.answer_ids.push(this.selected);
					this.selected = null;
				}
			} else {
				this.answer_ids.push(...this.checked);
				this.checked = [];
			}
			if (!this.answer_ids) {
				return;
			}
			axios
				.post(this.path, {
					answers: this.answer_ids,
					question_id: this.question.id,
				})
				.then((res) => {
					if (res.data.error) {
						this.error = res.data["error"];
					} else {
						this.getNextQuestion();
					}
				})
				.catch((error) => {
					// eslint-disable-next-line
					this.error = error.message;
					console.error(error);
				});
			if (
				!this.answered_questions.length ||
				this.answered_questions.indexOf(this.question.id) == -1
			) {
				$("#q_" + this.count).attr("data-q-id", this.question.id);
				this.answered_questions.push(this.question.id);
				this.count += 1;
			}
		},
		getAttempt() {
			axios
				.get(this.attemptPath)
				.then((res) => {
					this.attempt = res.data;
					for (let i = 0; i < this.attempt.answer_attempts.length; i++) {
						let question_id = this.attempt.answer_attempts[i]["question"];
						if (this.answered_questions.indexOf(question_id) == -1)
							this.answered_questions.push(question_id);
					}
				})
				.catch((error) => {
					this.error = error.message;
					console.error(error);
				});
		},
	},
	computed: {
		path() {
			return `/api/attempt/${this.attemptId}/question/`;
		},
		attemptPath() {
			return `/api/attempt/${this.attemptId}`;
		},
	},
	created() {
		this.getAttempt();
		this.getNextQuestion();
	},
};
</script>
