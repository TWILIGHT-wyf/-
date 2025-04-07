<template>
  <div class="container">
    <div class="login_box" v-show="target == 1">
      <div class="head">外卖管理平台</div>
      <!-- 登录 -->
      <el-form
        label-width="0"
        class="login_form"
        :model="login_form"
        :rules="login_rules"
        ref="login_form"
      >
        <!-- 手机号 -->
        <el-form-item prop="PhoneNumber">
          <el-input
            v-model="login_form.PhoneNumber"
            spellcheck="false"
            placeholder="手机号"
            prefix-icon="el-icon-phone"
          >
          </el-input>
        </el-form-item>
        <!-- 密码 -->
        <el-form-item prop="password">
          <el-input
            v-model="login_form.password"
            show-password
            spellcheck="false"
            placeholder="密码"
            prefix-icon="el-icon-lock"
          >
          </el-input>
        </el-form-item>

        <!-- 按钮 -->
        <el-form-item class="btns">
          <el-button type="primary" @click="llogin()">登录</el-button>
        </el-form-item>
      </el-form>
      <div>
        <div class="operate">
          <span id="op1" @click="change(2)">注册</span>
        </div>
      </div>
    </div>

    <!-- 注册表单 -->
    <div class="reg_box" v-show="target == 2">
      <div class="head">外卖管理平台</div>
      <el-form
        label-width="0"
        class="reg_form"
        :model="reg_form"
        :rules="reg_rules"
        ref="reg_form"
      >
        <!-- 用户名 -->
        <el-form-item prop="username">
          <el-input
            v-model="reg_form.username"
            spellcheck="false"
            placeholder="用户名"
            prefix-icon="el-icon-user"
          >
          </el-input>
        </el-form-item>
        <!-- 密码 -->
        <el-form-item prop="password">
          <el-input
            v-model="reg_form.password"
            show-password
            spellcheck="false"
            placeholder="密码(包含大小写字母、数字，长度在6-12之间)"
            prefix-icon="el-icon-lock"
          >
          </el-input>
        </el-form-item>
        <!-- 手机号 -->
        <el-form-item prop="telephone">
          <el-input
            v-model="reg_form.telephone"
            spellcheck="false"
            placeholder="手机号码"
            prefix-icon="el-icon-phone"
          >
          </el-input>
        </el-form-item>
        <!-- 角色 -->
        <el-form-item prop="role">
          <el-select v-model="reg_form.role" placeholder="请选择用户类型">
            <el-option label="客户" value="Customer"></el-option>
            <el-option label="商家" value="Vendor"></el-option>
            <el-option label="骑手" value="Rider"></el-option>
          </el-select>
        </el-form-item>
        <!-- 按钮 -->
        <el-form-item class="btns">
          <el-button type="primary" @click="zhuce()">注册</el-button>
          <el-button @click="change(1)">返回登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: "MyLogin",
  data() {
    var checkPassword = (rule, value, cb) => {
      const regPassword = /(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,12}$/;
      if (regPassword.test(value)) {
        return cb();
      }
      cb(new Error("包含大写字母、小写字母、数字，长度在6-12位之间"));
    };
    var checkMobile = (rule, value, cb) => {
      const regMobile = /^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$/;
      if (regMobile.test(value)) {
        return cb();
      }
      cb(new Error("手机号码格式不正确"));
    };
    return {
      target: 1,
      login_form: {
        PhoneNumber: "", // 修改为 PhoneNumber
        password: "",
      },
      reg_form: {
        username: "",
        password: "",
        telephone: "",
        role: "",
      },
      findback_form: {
        telephone: "",
        password: "",
      },
      login_rules: {
        PhoneNumber: [
          { required: true, message: "请输入电话", trigger: "blur" },
          { validator: checkMobile, trigger: "blur" },
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
      reg_rules: {
        username: [{ required: true, message: "请设置用户名", trigger: "blur" }],
        password: [
          { required: true, message: "请设置密码", trigger: "blur" },
          { validator: checkPassword, trigger: "blur" },
        ],
        telephone: [
          { required: true, message: "请绑定手机号", trigger: "blur" },
          { validator: checkMobile, trigger: "blur" },
        ],
        role: [{ required: true, message: "请选择用户类型", trigger: "change" }],
      },
      findback_rules: {
        telephone: [
          { required: true, message: "请输入电话", trigger: "blur" },
          { validator: checkMobile, trigger: "blur" },
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
    };
  },
  methods: {
    findback() {
      this.$refs.findback_form.validate((valid) => {
        if (!valid) return;
        else {
          console.log(111);
        }
      });
    },
    zhuce() {
      console.log("注册按钮被点击了");
      this.$refs.reg_form.validate((valid) => {
        if (!valid) return;
        else {
          this.$axios
            .request({
              method: "POST",
              url: "/api/user/register", // 修改为正确的后端接口地址
              data: {
                username: this.reg_form.username,
                password: this.reg_form.password,
                telephone: this.reg_form.telephone,
                role: this.reg_form.role,
              },
            })
            .then((res) => {
              if (res.data.status == 200) {
                this.$message({
                  message: "注册成功",
                  type: "success",
                });
                this.target = 1;
              } else {
                this.$message({
                  message: res.data.msg,
                  type: "error",
                });
              }
            })
            .catch((error) => {
              console.error("注册失败:", error);
              this.$message({
                message: "注册失败，请稍后再试",
                type: "error",
              });
            });
        }
      });
    },

    change(id) {
      this.target = id;
    },
    llogin() {
      this.$refs.login_form.validate((valid) => {
        if (!valid) return;
        else this.login();
      });
    },

    async login() {
      this.$axios
        .post("/api/user/login", {
          PhoneNumber: this.login_form.PhoneNumber,
          password: this.login_form.password,
        })
        .then((res) => {
          if (res.data.status != 200) {
            return this.$message({
              message: res.data.message, // 确保这里使用 res.data.message
              type: "error",
            });
          } else {
            this.$message({
              message: "登录成功",
              type: "success",
            });

            window.localStorage.setItem("token", res.data.token); // 确保后端返回了 token
            window.localStorage.setItem("user_id", res.data.user_id); // 存储 user_id

            // 存储 RiderID 如果存在
            if (res.data.role === "Rider" && res.data.rider_id) {
              window.localStorage.setItem("rider_id", res.data.rider_id); // 存储 RiderID
            }

            let routeName = "";
            switch (res.data.role) {
              case "Customer":
                routeName = "UserWYF";
                break;
              case "Vendor":
                routeName = "ShopWYF";
                break;
              case "Rider":
                routeName = "RiderWYF";
                break;
              default:
                this.$message({
                  message: "未知的用户类型",
                  type: "error",
                });
                this.$router.push("/");
                return;
            }

            this.$router.push({ name: routeName });
          }
        })
        .catch(() => {
          this.$message({
            message: "手机号或密码错误",
            type: "error",
          });
        });
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.login_box,
.reg_box {
  width: 400px;
  padding: 20px;
  background: #fff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.head {
  text-align: center;
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.login_form,
.reg_form {
  width: 100%;
}

.el-form-item {
  width: 350px;
  margin-left: 50px;
}

.el-input,
.el-select {
  border-radius: 5px;
}

.el-button {
  width: 100%;
  border-radius: 5px;
  background-color: #409eff;
  color: #fff;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.el-button:hover {
  background-color: #66b1ff;
}

.btns {
  text-align: center;
}

.operate {
  text-align: center;
  color: #000;
  opacity: 0.7;
  font-weight: 400;
  font-size: 16px;
  margin-left: 28px;
}

#op1 {
  padding-left: 15px;
  padding-right: 30px;
  border-right: 1px solid #bdb9b9;
  cursor: pointer;
  transition: color 0.3s ease;
}

#op1:hover {
  color: #409eff;
}
</style>
