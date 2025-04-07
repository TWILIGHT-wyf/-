<template>
  <div>
    <div class="header">&nbsp;&nbsp; 外卖管理平台</div>
    <div class="body">
      <!-- 左侧导航栏 -->
      <div class="liner">
        <el-menu
          default-active="1"
          class="el-menu-vertical-demo"
          background-color="#ffffff"
          text-color="#333"
          active-text-color="#409EFF"
          @select="handleSelect"
        >
          <el-menu-item index="1">
            <i class="el-icon-menu"></i>
            <span slot="title">逛店铺</span>
          </el-menu-item>

          <el-submenu index="2">
            <template slot="title">
              <i class="el-icon-setting"></i>
              <span>个人订单</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="3">已完成订单</el-menu-item>
              <el-menu-item index="4">已发货订单</el-menu-item>
              <el-menu-item index="5">未发货订单</el-menu-item>
            </el-menu-item-group>
          </el-submenu>

          <el-submenu index="6">
            <template slot="title">
              <i class="el-icon-s-home"></i>
              <span>个人中心</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="7">个人信息</el-menu-item>
              <el-menu-item index="8">修改密码</el-menu-item>
            </el-menu-item-group>
          </el-submenu>
        </el-menu>
      </div>
      <div class="main">
        <div id="usershop" v-show="active === '1'">
          <usershop :shops="shops" />
        </div>

        <div id="userfinished" v-show="active === '3'">
          <userfinished />
        </div>

        <div id="usersending" v-show="active === '4'">
          <usersending />
        </div>

        <div id="userunsend" v-show="active === '5'">
          <userunsend />
        </div>

        <div id="indimag" v-show="active === '7'">
          <indimsg />
        </div>

        <div id="changepwd" v-show="active === '8'">
          <changepwd />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import usershop from "@/components_wyf/User_wyf/Userorder_wyf.vue";
import userfinished from "@/components_wyf/User_wyf/UserFinished_wyf.vue";
import usersending from "@/components_wyf/User_wyf/UserSending_wyf.vue";
import userunsend from "@/components_wyf/User_wyf/UserUnsend_wyf.vue";
import indimsg from "@/components_wyf/User_wyf/userinformation_wyf.vue";
import changepwd from "@/components_wyf/User_wyf/chpassword_wyf.vue";

export default {
  components: {
    usershop,
    userfinished,
    usersending,
    userunsend,
    indimsg,
    changepwd,
  },
  data() {
    return {
      active: "1", // 初始激活的菜单项
      shops: [], // 存储商家信息
    };
  },
  methods: {
    getShops() {
      this.$axios
        .get("/api/user/allshops", {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.shops = res.data.tabledata;
          }
        })
        .catch((error) => {
          console.error("Error fetching shops:", error);
        });
    },
    handleSelect(index) {
      this.active = index;
      if (index === "1") {
        this.getShops();
      }
    },
  },
  mounted() {
    this.getShops(); // 页面加载时获取商家信息
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
