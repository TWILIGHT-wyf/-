<template>
  <div>
    <div class="header">个人信息</div>
    <div class="body">
      <el-form ref="form" :model="form" label-width="20%" id="selectForm">
        <el-form-item label="用户名：" prop="Username">
          <el-input v-model="form.Username"></el-input>
        </el-form-item>
        <el-form-item label="真实姓名：" prop="RealName">
          <el-input v-model="form.RealName"></el-input>
        </el-form-item>
        <el-form-item label="年龄：" prop="Age">
          <el-input v-model="form.Age"></el-input>
        </el-form-item>
        <el-form-item label="性别：" prop="Gender">
          <el-input v-model="form.Gender"></el-input>
        </el-form-item>
        <el-form-item label="地址：" prop="Address">
          <el-input v-model="form.Address"></el-input>
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="updateUserInfo">保存修改</el-button>
    </div>
  </div>
</template>

<script>
export default {
  created() {
    this.getdata();
  },
  data() {
    return {
      form: {
        RealName: "",
        Gender: "",
        Age: "",
        Address: "",
        Username: "",
      },
    };
  },
  methods: {
    getdata() {
      const token = localStorage.getItem("token");
      this.$axios
        .get("/api/user/usermsg", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.form.Age = res.data.data.Age;
            this.form.RealName = res.data.data.RealName;
            this.form.Gender = res.data.data.Gender;
            this.form.Address = res.data.data.Address;
            this.form.Username = res.data.data.Username;
          }
        })
        .catch((error) => {
          console.error("Error fetching user data:", error);
        });
    },
    updateUserInfo() {
      const token = localStorage.getItem("token");
      this.$axios
        .put("/api/user/update", this.form, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.$message.success("用户信息更新成功");
          } else {
            this.$message.error("用户信息更新失败");
          }
        })
        .catch((error) => {
          console.error("Error updating user info:", error);
        });
    },
  },
};
</script>

<style scoped>
.header {
  width: 100%;
  height: 10%;
  text-align: center;
  line-height: 64px;
  font-size: 20px;
  font-weight: 800;
  border-bottom: 1px solid #e3e3e3;
}

.body {
  width: 40%;
  margin-top: 30px;
  margin-left: 30px;
}

#selectForm >>> .el-form-item__label {
  font-size: 18px;
}

.el-input {
  font-size: 18px;
}
</style>
