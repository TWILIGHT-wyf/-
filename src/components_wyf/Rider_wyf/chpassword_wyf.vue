<template>
  <div>
    <div class="header">修改密码</div>
    <div class="body">
      <el-form
        ref="form"
        :model="form"
        label-width="23%"
        id="selectForm"
        :rules="form_rules"
      >
        <el-form-item label="原密码：" prop="old_pwd">
          <el-input v-model="form.old_pwd" type="password" show-password></el-input>
        </el-form-item>

        <el-form-item label="新密码：" prop="new_pwd">
          <el-input v-model="form.new_pwd" type="password" show-password></el-input>
        </el-form-item>

        <el-form-item label="确认密码：" prop="check_pwd">
          <el-input v-model="form.check_pwd" type="password" show-password></el-input>
        </el-form-item>
        <el-form-item style="text-align: center">
          <el-button type="primary" @click="change()">确定</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        old_pwd: "",
        new_pwd: "",
        check_pwd: "",
      },
      form_rules: {
        old_pwd: [{ required: true, message: "必填", trigger: "blur" }],
        new_pwd: [{ required: true, message: "必填", trigger: "blur" }],
        check_pwd: [{ required: true, message: "必填", trigger: "blur" }],
      },
    };
  },
  methods: {
    change() {
      this.$refs.form.validate((valid) => {
        if (!valid) return;
        if (this.form.check_pwd !== this.form.new_pwd) {
          this.$message.error("新密码与确认密码不一致");
          return;
        }
        this.$axios
          .post("/api/user/pwd_chg", this.form, {
            headers: {
              Authorization: localStorage.getItem("token"),
            },
          })
          .then((res) => {
            if (res.data.status === 200) {
              this.$message.success(res.data.message);
            } else {
              this.$message.error(res.data.message);
            }
          })
          .catch(() => {
            this.$message.error("修改密码失败");
          });
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

span {
  font-size: 18px;
}
</style>
