<template>
  <v-container class="grid">
    <masonry :cols="3" :gutter="30">
      <div v-for="game in games">
        <Card :id="game.id" :title="game.name" :description="game.description" :genres="game.genres"
              :img_url="game.img_url" :like_action="undefined" :dislike_action="undefined" :show_like="false"
              :show_dislike="false" show_link="true"/>
      </div>
    </masonry>
  </v-container>
</template>

<script>
    import Card from '~/components/Card.vue'

    export default {
        components: {
            Card
        },
        data() {
            return {
                games: []
            }
        },
        props: {},
        methods: {
            async getRecommendation() {
                let response = await this.$axios.post('/games/recommendation')
                console.log(response.data)
                let data = JSON.parse(response.data['recommendation'])
                for (let i = 0; i < data.length; i++) {
                    let game = data[i]
                    this.games.push({
                        "id": game.appid,
                        "name": game.name,
                        "description": game.short_description.replace('&quot;', '').replace('&amp;', '').replace('&nbsp;', ''),
                        "genres": game.genres.split(";").join(", "),
                        "img_url": game.header_image
                    })
                }
            }
        },
        created() {
            this.getRecommendation()
        },
        middleware: 'auth'
    }
</script>

<style scoped>
  .grid {
    margin-top: 48px;
  }
</style>
