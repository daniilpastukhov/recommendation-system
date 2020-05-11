<template>
  <v-content>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12">
          <v-container class="headline">
            This application is a semester work for subject BI-VWM.
            <div class="body-1">Author: Daniil Pastukhov</div>
          </v-container>
          <v-container>
            <v-btn-toggle rounded>
              <v-btn to="/rate" color="white" >Rate games</v-btn>
              <v-btn to="/recommend" color="white">Get recommendations</v-btn>
            </v-btn-toggle>
          </v-container>
        </v-col>
      </v-row>
    </v-container>
  </v-content>
</template>

<script>
    import Menu from '~/components/Menu.vue'
    import SideMenu from '~/components/SideMenu.vue'
    import Grid from '~/components/Grid.vue'

    export default {
        components: {
            Menu,
            SideMenu,
            Grid
        },
        data() {
            return {}
        },
        methods: {}
    }
</script>

<style>
  .container {
    margin: 0 auto;
    width: 100%;
    text-align: center;
  }

  .post {
    margin: 25px auto;
  }

  .post p {
    margin: 0px;
    padding: 0px;
  }

  .title {
    font-family: 'Quicksand', 'Source Sans Pro', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    display: block;
    font-weight: 300;
    font-size: 100px;
    color: #35495e;
    letter-spacing: 1px;
  }

  /* body {
    margin-top: 64px;
  } */

</style>
