<template>
  <v-row class="grid">
    <v-col cols="6" class="justify-center grid-col">
      <div class="display-1 font-weight-light">Games you like</div>
      <masonry :cols="2" :gutter="30">
        <div v-for="game in games['likes']">
          <Card :id="game.id" :title="game.name" :description="game.description" :genres="game.genres"
                :img_url="game.img_url" :like_action="like" :dislike_action="dislike" :delete_action="delete_game"
                :show_delete="true" :show_like="false" :show_dislike="true"/>
        </div>
      </masonry>
    </v-col>
    <v-col cols="6" class="justify-center grid-col">
      <div class="display-1 font-weight-light">Games you don't like</div>
      <masonry :cols="2" :gutter="30">
        <div v-for="game in games['dislikes']">
          <Card :id="game.id" :title="game.name" :description="game.description" :genres="game.genres"
                :img_url="game.img_url" :like_action="like" :dislike_action="dislike" :show_dislike="false"
                :delete_action="delete_game" :show_delete="true" :show_like="true"/>
        </div>
      </masonry>
    </v-col>
  </v-row>
</template>

<script>
    import Card from '~/components/Card.vue'

    export default {
        components: {
            Card
        },
        data() {
            return {
                games: {
                    'likes': [],
                    'dislikes': []
                },
                loading: Boolean
            }
        },
        props: {},
        methods: {
            async getGames(type) {
                this.loading = true
                let response = await this.$axios.post('/games/list', {'type': type})
                let data = JSON.parse(response.data['games'])
                for (let i = 0; i < data.length; i++) {
                    let game = data[i]
                    this.games[type].push({
                        "id": game.appid,
                        "name": game.name,
                        "description": game.short_description.replace('&quot;', '').replace('&amp;', '').replace('&nbsp;', ''),
                        "genres": game.genres.split(';').join(', '),
                        "img_url": game.header_image
                    })
                }
                this.loading = false
            },
            async like(id) {
                await this.$axios.post('/games/like', {"id": id})
                this.games = {
                    'likes': [],
                    'dislikes': []
                }
                await this.getGames('likes')
                await this.getGames('dislikes')
            },
            async dislike(id) {
                await this.$axios.post('/games/dislike', {"id": id})
                this.games = {
                    'likes': [],
                    'dislikes': []
                }
                await this.getGames('likes')
                await this.getGames('dislikes')
            },
            async delete_game(id) {
                await this.$axios.post('/games/delete', {"id": id})
                this.games = {
                    'likes': [],
                    'dislikes': []
                }
                await this.getGames('likes')
                await this.getGames('dislikes')
            }
        },
        mounted() {
            this.getGames('likes')
            this.getGames('dislikes')
        },
        middleware: 'auth'
    }
</script>

<style lang="scss" scoped>
  .grid {
    margin: 48px 16px 0 16px;
  }

  .grid-col {
    padding-left: 15px;
    padding-right: 15px;
  }

  .load_button {
    margin: 32px 0;
  }

  .v-card__actions {

    .like_button {
      background-color: green !important;
    }

    .dislike_button {
      background-color: red !important;
    }
  }
</style>
