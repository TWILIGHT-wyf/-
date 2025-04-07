<template>
  <div class="container">
    <div class="header">商家管理</div>
    <div class="body">
      <div class="sidebar">
        <el-menu
          default-active="1"
          class="el-menu-vertical-demo"
          background-color="#ffffff"
          text-color="#333"
          active-text-color="#409EFF"
          @select="handleSelect"
        >
          <el-menu-item index="1">
            <i class="el-icon-s-shop"></i>
            <span slot="title">店铺管理</span>
          </el-menu-item>

          <el-menu-item index="2">
            <i class="el-icon-s-custom"></i>
            <span slot="title">菜品管理</span>
          </el-menu-item>

          <el-submenu index="100">
            <template slot="title">
              <i class="el-icon-s-order"></i>
              <span>订单管理</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="6">已完成订单</el-menu-item>
              <el-menu-item index="7">已发货订单</el-menu-item>
              <el-menu-item index="8">未发货订单</el-menu-item>
            </el-menu-item-group>
          </el-submenu>

          <el-menu-item index="4">
            <i class="el-icon-s-tools"></i>
            <span slot="title">修改密码</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="main">
        <transition name="fade" mode="out-in">
          <div id="shopinformation_wyf" v-if="active == 1">
            <shopinformation_wyf></shopinformation_wyf>
          </div>

          <div id="dish_wyf" v-if="active == 2">
            <dish_wyf></dish_wyf>
          </div>

          <div id="ordersended" v-if="active == 6">
            <ordersended></ordersended>
          </div>
          <div id="ordersending" v-if="active == 7">
            <ordersending></ordersending>
          </div>

          <div id="orderunsend" v-if="active == 8">
            <orderunsend></orderunsend>
          </div>

          <div id="chpassword_wyf" v-if="active == 4">
            <chpassword_wyf></chpassword_wyf>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import shopinformation_wyf from "@/components_wyf/Shop_wyf/shopinformation_wyf.vue";
import dish_wyf from "@/components_wyf/Shop_wyf/dish_wyf.vue";
import ordersended from "@/components_wyf/Shop_wyf/BeSended_wyf.vue";
import ordersending from "@/components_wyf/Shop_wyf/BeSending_wyf.vue";
import orderunsend from "@/components_wyf/Shop_wyf/UnSend_wyf.vue";
import chpassword_wyf from "@/components_wyf/Shop_wyf/chpassword_wyf.vue";

export default {
  components: {
    shopinformation_wyf,
    dish_wyf,
    ordersended,
    ordersending,
    orderunsend,
    chpassword_wyf,
  },
  data() {
    return {
      active: 1,
    };
  },
  methods: {
    handleSelect(index) {
      this.active = parseInt(index);
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  width: 100%;
  height: 10vh;
  line-height: 10vh;
  font-size: 25px;
  font-weight: 800;
  background-color: #ffffff;
  border-bottom: 1px solid #e3e3e3;
  padding-left: 20px; /* 调整左侧内边距 */
}

.body {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 200px;
  background-color: #ffffff;
  border-right: 1px solid #e3e3e3;
}

.main {
  flex: 1;
  padding: 20px;
  background-color: #f5f5f5;
  overflow-y: auto;
}
</style>
