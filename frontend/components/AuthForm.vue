<template>
  <v-app id="inspire">
    <v-content>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <v-card class="elevation-12">
              <v-toolbar color="primary" dark flat>
                <v-toolbar-title>{{ title }}</v-toolbar-title>
                <!-- <v-spacer /> -->
                <!-- <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-btn :href="source" icon large target="_blank" v-on="on">
                      <v-icon>mdi-code-tags</v-icon>
                    </v-btn>
                  </template>
                  <span>Source</span>
                </v-tooltip> -->
                <!-- <v-tooltip right>
                  <template v-slot:activator="{ on }">
                    <v-btn icon large href="https://codepen.io/johnjleider/pen/pMvGQO" target="_blank" v-on="on">
                      <v-icon>mdi-codepen</v-icon>
                    </v-btn>
                  </template>
                  <span>Codepen</span>
                </v-tooltip> -->
              </v-toolbar>
              <v-card-text>
                <div @keydown.enter="submitForm(userInfo)">
                  <v-form v-model="valid">
                    <v-text-field v-model="userInfo.username"
                                  label="Name" name="name" prepend-icon="person"
                                  :rules="[required('name')]"
                                  v-if="hasName"/>

                    <v-text-field label="Email" name="login" prepend-icon="email" type="text"
                                  v-model="userInfo.email"
                                  :rules="[required('email'), emailFormat()]"/>

                    <v-text-field id="password" label="Password" name="password" prepend-icon="lock"
                                  v-model="userInfo.password"
                                  :type="showPassword ? 'text' : 'password'"
                                  :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                                  @click:append="showPassword = !showPassword" counter=true
                                  :rules="[required('password'), minLength('password', 8)]"/>
                  </v-form>
                </div>
              </v-card-text>
              <v-card-actions>
                <v-spacer/>
                <span class="error_message">{{ $store.state.login_status }}</span>
                <v-btn @click="submitForm(userInfo)" :disabled="!valid" color="primary">{{ buttonText }}</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
    import validations from "~/utils/validations";

    export default {
        data() {
            return {
                valid: false,
                showPassword: false,
                userInfo: {
                    username: '',
                    email: '',
                    password: '',
                    type: 'email'
                },
                ...validations
            }
        },
        props: {
            submitForm: {
                type: Function,
                required: true
            },
            buttonText: {
                type: String,
                required: true
            },
            title: {
                String,
                required: true
            },
            hasName: Boolean,
        }
    }

</script>

<style lang="scss" scoped>
  .error_message {
    margin-right: 10px;
    font-size: 14px;
    color: #ff5252 !important;
  }

</style>
