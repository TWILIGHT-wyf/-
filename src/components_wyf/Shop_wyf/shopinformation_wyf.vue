<template>
  <div>
    <div class="header">商家管理</div>
    <div class="body">
      <el-table :data="tableData" style="width: 89%" class="table">
        <el-table-column
          prop="shop_name"
          label="店铺名称"
          width="200"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="address"
          label="店铺地址"
          width="200"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="description"
          label="店铺简介"
          width="200"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="contact"
          label="联系方式"
          width="200"
          align="center"
        ></el-table-column>
        <el-table-column prop="operate" label="操作" width="200" align="center">
          <template slot-scope="scope">
            <el-button size="small" type="warning" @click="showdia_chg(scope.row)"
              >修改</el-button
            >
          </template>
        </el-table-column>
        <el-table-column v-if="!hasShop" width="120" align="center">
          <template slot="header">
            <el-button
              icon="el-icon-plus"
              size="small"
              type="success"
              @click="showdia_add()"
              >添加店铺</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加店铺对话框 -->
      <el-dialog title="添加店铺" :visible.sync="dia_add" width="30%">
        <el-form
          ref="add_form"
          :model="add_form"
          label-width="100px"
          :rules="add_form_rules"
        >
          <el-form-item label="店铺名称：" prop="shop_name">
            <el-input v-model="add_form.shop_name"></el-input>
          </el-form-item>
          <el-form-item label="店铺地址：" prop="address">
            <el-input v-model="add_form.address"></el-input>
          </el-form-item>
          <el-form-item label="店铺简介：" prop="description">
            <el-input v-model="add_form.description" type="textarea" :rows="4"></el-input>
          </el-form-item>
          <el-form-item label="联系方式：" prop="contact">
            <el-input v-model="add_form.contact"></el-input>
          </el-form-item>
        </el-form>
      </el-dialog>

      <!-- 修改店铺对话框 -->
      <el-dialog title="修改店铺" :visible.sync="dia_chg" width="30%">
        <el-form ref="form" :model="chg_form" label-width="100px">
          <el-form-item label="店铺名称：">
            <el-input v-model="chg_form.shop_name"></el-input>
          </el-form-item>
          <el-form-item label="店铺地址：">
            <el-input v-model="chg_form.address"></el-input>
          </el-form-item>
          <el-form-item label="店铺简介：">
            <el-input v-model="chg_form.description" type="textarea" :rows="4"></el-input>
          </el-form-item>
          <el-form-item label="联系方式：">
            <el-input v-model="chg_form.contact"></el-input>
          </el-form-item>
        </el-form>
      </el-dialog>
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
      tableData: [],
      dia_add: false,
      dia_chg: false,
      hasShop: false,
      add_form: {
        shop_name: "",
        address: "",
        description: "",
        contact: "",
        logo_image: null, // 新增字段
        action: "add",
      },
      chg_form: {
        shop_name: "",
        address: "",
        description: "",
        contact: "",
        logo_image: null, // 新增字段
        action: "change",
      },
      add_form_rules: {
        shop_name: [{ required: true, message: "必填项", trigger: "blur" }],
        address: [{ required: true, message: "必填项", trigger: "blur" }],
        description: [{ required: true, message: "必填项", trigger: "blur" }],
        contact: [{ required: true, message: "必填项", trigger: "blur" }],
      },
    };
  },
  methods: {
    getdata() {
      const token = localStorage.getItem("token");
      this.$axios
        .get("/api/manager/shop", {
          headers: {
            Authorization: token,
          },
        })
        .then((res) => {
          if (res.data.status === 200) {
            this.tableData = res.data.data;
            this.hasShop = this.tableData.length > 0; // 检查是否已有店铺
          } else {
            console.error("Failed to fetch shop data:", res.data.message);
          }
        })
        .catch((error) => {
          console.error("Error fetching shop data:", error);
        });
    },
    submitAddForm() {
      this.$refs.add_form.validate((valid) => {
        if (!valid) return;
        else {
          const formData = new FormData();
          formData.append("shop_name", this.add_form.shop_name);
          formData.append("address", this.add_form.address);
          formData.append("description", this.add_form.description);
          formData.append("contact", this.add_form.contact);
          formData.append("logo_image", this.add_form.logo_image); // 新增字段

          const token = localStorage.getItem("token");
          this.$axios
            .post("/api/manager/shop", formData, {
              headers: {
                "Content-Type": "multipart/form-data",
                Authorization: token,
              },
            })
            .then((res) => {
              if (res.data.status === 200) {
                this.$message({
                  message: "添加成功",
                  type: "success",
                });
                this.dia_add = false;
                this.getdata();
              } else {
                this.$message({
                  message: res.data.message,
                  type: "error",
                });
              }
            })
            .catch((error) => {
              console.error("Error adding shop:", error);
              this.$message({
                message: "添加失败",
                type: "error",
              });
            });
        }
      });
    },
    submitChgForm() {
      this.$refs.form.validate((valid) => {
        if (!valid) return;
        else {
          const formData = new FormData();
          formData.append("shop_name", this.chg_form.shop_name);
          formData.append("address", this.chg_form.address);
          formData.append("description", this.chg_form.description);
          formData.append("contact", this.chg_form.contact);
          formData.append("logo_image", this.chg_form.logo_image); // 新增字段

          const token = localStorage.getItem("token");
          this.$axios
            .put("/api/manager/shop", formData, {
              headers: {
                "Content-Type": "multipart/form-data",
                Authorization: token,
              },
            })
            .then((res) => {
              if (res.data.status === 200) {
                this.$message({
                  message: "修改成功",
                  type: "success",
                });
                this.dia_chg = false;
                this.getdata();
              } else {
                this.$message({
                  message: res.data.message,
                  type: "error",
                });
              }
            })
            .catch((error) => {
              console.error("Error updating shop:", error);
              this.$message({
                message: "修改失败",
                type: "error",
              });
            });
        }
      });
    },
    handleAddFileChange(file) {
      this.add_form.logo_image = file.raw;
    },
    handleChangeFileChange(file) {
      this.chg_form.logo_image = file.raw;
    },
    showdia_chg(row) {
      this.chg_form.shop_name = row.shop_name;
      this.chg_form.address = row.address;
      this.chg_form.description = row.description;
      this.chg_form.contact = row.contact;
      this.dia_chg = true;
    },
    showdia_add() {
      this.dia_add = true;
    },
    delshop(row) {
      this.$confirm("此操作将永久删除该店铺, 是否继续?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          const token = localStorage.getItem("token");
          this.$axios
            .delete("/api/manager/shop", {
              headers: {
                Authorization: token,
              },
              data: {
                shop_name: row.shop_name,
              },
            })
            .then((res) => {
              if (res.data.status === 200) {
                this.$message({
                  type: "success",
                  message: "删除成功!",
                });
                this.getdata();
              } else {
                this.$message({
                  type: "error",
                  message: res.data.message,
                });
              }
            })
            .catch((error) => {
              console.error("Error deleting shop:", error);
              this.$message({
                type: "info",
                message: "删除失败",
              });
            });
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "已取消删除",
          });
        });
    },
  },
};
</script>

<style scoped>
.header {
  font-size: 24px;
  margin-bottom: 20px;
}
.body {
  padding: 20px;
}
.table {
  margin-top: 20px;
}
</style>
