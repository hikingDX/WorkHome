<template>
  <div><h1>这是子组件:{{parentmsg}}</h1></div>
</template>

<script>
export default {
  name: 'comp1',
  data () {
    return {
      title: '123',
      content: 'qqq'
    }
  },
  props: ['parentmsg']// 把父组件传递过来的parentemsg属性，现在props数组中定义一下，这样才能使用
}
</script>

<style scoped>

</style>
