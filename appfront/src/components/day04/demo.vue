<template>
  <mycomp1 v-bind:parentmsg="msg"></mycomp1>
</template>

<script>
import comp1 from './comp1'

export default {
  name: 'demo',
  data () {
    return {
      msg: '父组件数据'
    }
  },
  components: {
    mycomp1: comp1
  }

}
</script>

<style scoped>

</style>
