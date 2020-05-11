export const state = () => ({
  login_status: "",
  search_status: false,
  search_text: ''
});

export const mutations = {
  SET_LOGIN_STATUS(state, value) {
    state.login_status = value
  },
  SET_SEARCH_STATUS(state, value) {
    state.search_status = value
  },
  SET_SEARCH_TEXT(state, value) {
    state.search_text = value
  }
};

