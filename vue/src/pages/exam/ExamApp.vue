<template>
  <div>
    <Timer :attempt-id="attemptId"></Timer>
    <Exam :attempt-id="attemptId"> </Exam>
  </div>
</template>

<script>
import Exam from "../../components/Exam.vue";
import Timer from "../../components/Timer.vue";

export default {
  props: {
    attemptId: String,
  },
  components: {
    Exam,
    Timer,
  },
};
</script>
