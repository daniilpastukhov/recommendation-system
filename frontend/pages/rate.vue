<template>
  <Grid />
</template>

<script>
  import Grid from '~/components/Grid.vue'

  export default {
        components: {
            Grid
        },
        data() {
          return {

          }
        },
        methods: {
            getNewFeed() {
                this.$axios.post('/api/feed', {
                    "filters": {},
                    "limit": 10
                }).then(response => {
                    this.posts.push(response['feed'])
                })
            }
        },
      middleware: 'auth'
    }
</script>
