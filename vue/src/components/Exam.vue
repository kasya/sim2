<template>
  <div>
    <div v-if="error">{{ error }}</div>
    <div id="wrapper">
      <h4>{{ question.text }}</h4>
      <form class="form-check">
        <div>
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
              <label v-bind:for="a.id">{{ a.text }}</label>
            </li>
          </ul>
        </div>

        <div id="flag">
          <input
            id="flag"
            type="checkbox"
            v-on:click="toggleQuestion"
            v-model="activeFlag"
          />
          <label for="flag">Come back to this question later</label>
        </div>
      </form>
      <div v-show="correct_answers_text.length > 0">
        Oops! You've made a mistake. You should have picked:
        <p v-for="text in correct_answers_text" v-bind:key="text">
          • {{ text }}
        </p>
      </div>
      <div v-show="result == 'correct'">
        Everything correct! Good job!
        <p v-for="text in correct_answers_text" v-bind:key="text">
          • {{ text }}
        </p>
      </div>

      <div v-show="attempt.mode == 1">
        <button
          class="btn bg-gradient-info w-auto me-1 mb-0"
          type="button"
          v-on:click="checkAnswer"
          v-show="question.text"
          :disabled="!selected && !checked.length"
        >
          Check answer
        </button>
      </div>
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
            <span
              class="flag"
              v-show="flaggedQuestions.indexOf(answeredQuestions[i - 1]) != -1"
            >
              🔴
            </span>
            <a
              class="page-link"
              href="#"
              @click="getQuestion"
              v-bind:id="'q_' + i"
              :data-q-id="answeredQuestions[i - 1]"
              >{{ i }}</a
            >
          </li>
        </ul>
      </nav>
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
      answeredQuestions: [],
      attempt: {},
      checked: [],
      correct_answers_text: "",
      count: 1,
      error: null,
      flaggedQuestions: [],
      activeFlag: false,
      isChecked: false,
      result: false,
      selected: null,
      question: {},
      questionId: -1,
      multipleChoice: "multiple_choice",
    };
  },
  methods: {
    getNextQuestion() {
      this.activeFlag = false;
      this.correct_answers_text = "";
      this.error = "";
      this.isChecked = false;
      this.result = false;
      axios
        .get(this.path)
        .then((res) => {
          if (res.data.id) {
            this.question = res.data;
          } else if (this.flaggedQuestions.length > 0) {
            /* after all questions has been answered, go through flagged questions */
            this.getQuestion(undefined, this.flaggedQuestions.shift());
          } else {
            window.location.href = `/exam/${this.attemptId}/finish`;
          }
        })
        .catch((error) => {
          this.error = error.response.data.message;
          console.error(error.response);
        });
    },
    getQuestion(event, id) {
      this.result = false;
      this.flaggedQuestions.push(id);
      if (event === undefined) {
        this.questionId = parseInt(id);
      }
      if (id === undefined) {
        this.questionId = parseInt($(event.target).attr("data-q-id"));
      }
      axios
        .get(`/api/attempt/${this.attemptId}/${this.questionId}`)
        .then((res) => {
          if (res.data["question"]) {
            this.question = res.data["question"];
            this.activeFlag =
              this.flaggedQuestions.indexOf(this.question.id) != -1;

            if (this.question.type == this.multipleChoice) {
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
      this.answerIds = [];
      this.correct_answers_text = "";

      if (this.question.type == this.multipleChoice) {
        if (this.selected != null) {
          this.answerIds.push(this.selected);
          this.selected = null;
        }
      } else {
        this.answerIds.push(...this.checked);
        this.checked = [];
      }
      if (!this.answerIds) {
        return;
      }
      axios
        .post(this.checkAnswerPath, {
          answer_ids: this.answerIds,
          question_id: this.question.id,
        })
        .then((res) => {
          this.result = res.data["result"];
          if (res.data["correct_answers"]) {
            this.correct_answers_text = res.data["correct_answers"];
          }
          if (this.question.type == this.multipleChoice) {
            this.selected = this.answerIds[0];
          } else {
            this.checked = this.answerIds;
          }
        })
        .catch((error) => {
          this.error = error.response.data.message;
          console.error(error.response);
        });
    },
    toggleQuestion() {
      axios
        .post(`/api/attempt/${this.attemptId}/${this.question.id}/flag`)
        .then((res) => {
          this.flaggedQuestions = res.data["flagged_questions"];
        })
        .catch((error) => {
          this.error = error.response.data.message;
          console.error(error.response);
        });
    },
    recordAnswer() {
      this.answerIds = [];
      if (this.question.type == this.multipleChoice) {
        if (this.selected != null) {
          this.answerIds.push(this.selected);
          this.selected = null;
        }
      } else {
        this.answerIds.push(...this.checked);
        this.checked = [];
      }
      if (!this.answerIds) {
        return;
      }
      axios
        .post(this.path, {
          answers: this.answerIds,
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
        !this.answeredQuestions.length ||
        this.answeredQuestions.indexOf(this.question.id) == -1
      ) {
        $("#q_" + this.count).attr("data-q-id", this.question.id);
        this.answeredQuestions.push(this.question.id);
        this.count += 1;
      }
    },
    getAttempt() {
      axios
        .get(this.attemptPath)
        .then((res) => {
          this.attempt = res.data;
          this.flaggedQuestions = res.data["flagged_questions"];
          for (let i = 0; i < this.attempt.answer_attempts.length; i++) {
            let questionId = this.attempt.answer_attempts[i]["question"];
            if (this.answeredQuestions.indexOf(questionId) == -1)
              this.answeredQuestions.push(questionId);
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
    checkAnswerPath() {
      return `/api/${this.question.id}/check_answer/`;
    },
  },
  created() {
    this.getAttempt();
    this.getNextQuestion();
  },
};
</script>
