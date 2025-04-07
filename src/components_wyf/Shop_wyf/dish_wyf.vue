<template>
  <div>
    <div class="header">菜品管理</div>
    <div class="body">
      <el-table :data="tableData" style="width: 89%" class="table">
        <el-table-column prop="DishName" label="菜品名称" width="200" align="center">
        </el-table-column>
        <el-table-column prop="QuantityInStock" label="余量" width="200" align="center">
        </el-table-column>
        <el-table-column prop="Description" label="描述" width="200" align="center">
        </el-table-column>
        <el-table-column prop="UnitPrice" label="单价" width="200" align="center">
        </el-table-column>
        <el-table-column prop="operate" label="操作" width="200" align="center">
          <template slot-scope="scope">
            <el-button size="small" type="warning" @click="showdia_update(scope.row)"
              >更新</el-button
            >
            <el-button size="small" type="danger" @click="showdia_dlt(scope.row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
        <el-table-column width="120" align="center">
          <template slot="header">
            <el-button
              icon="el-icon-plus"
              size="small"
              type="success"
              @click="showdia_add()"
              >添加菜品</el-button
            >
          </template>
        </el-table-column>
      </el-table>
      <el-dialog title="更新菜品" :visible.sync="dia_update" width="30%">
        <el-form
          ref="update_form"
          :model="update_form"
          label-width="120px"
          :rules="update_form_rules"
        >
          <el-form-item label="菜品名称：" prop="DishName">
            <el-input v-model="update_form.DishName"></el-input>
          </el-form-item>
          <el-form-item label="余量：" prop="QuantityInStock">
            <el-input v-model="update_form.QuantityInStock"></el-input>
          </el-form-item>
          <el-form-item label="描述：" prop="Description">
            <el-input v-model="update_form.Description" type="textarea"></el-input>
          </el-form-item>
          <el-form-item label="单价：" prop="UnitPrice">
            <el-input v-model="update_form.UnitPrice"></el-input>
          </el-form-item>
        </el-form>
        <div style="text-align: center">
          <el-button type="primary" @click="updatedish()"> 更新 </el-button>
        </div>
      </el-dialog>
      <el-dialog title="添加菜品" :visible.sync="dia_add" width="30%">
        <el-form
          ref="add_form"
          :model="add_form"
          label-width="120px"
          :rules="add_form_rules"
        >
          <el-form-item label="菜品名称：" prop="DishName">
            <el-input v-model="add_form.DishName"></el-input>
          </el-form-item>
          <el-form-item label="余量：" prop="QuantityInStock">
            <el-input v-model="add_form.QuantityInStock"></el-input>
          </el-form-item>
          <el-form-item label="描述：" prop="Description">
            <el-input v-model="add_form.Description" type="textarea"></el-input>
          </el-form-item>
          <el-form-item label="单价：" prop="UnitPrice">
            <el-input v-model="add_form.UnitPrice"></el-input>
          </el-form-item>
        </el-form>
        <div style="text-align: center">
          <el-button type="primary" @click="adddish()"> 添加 </el-button>
        </div>
      </el-dialog>

      <el-dialog title="删除菜品" :visible.sync="dia_dlt" width="30%">
        <div>确定删除此菜品吗？</div>
        <div style="text-align: center">
          <el-button type="primary" @click="deletedish()"> 确定 </el-button>
        </div>
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
      dia_dlt: false,
      dia_update: false, // 新增更新对话框状态
      add_form: {
        DishName: "",
        QuantityInStock: "",
        Description: "",
        UnitPrice: "",
      },
      update_form: {
        // 新增更新表单数据
        DishID: "",
        DishName: "",
        QuantityInStock: "",
        Description: "",
        UnitPrice: "",
      },
      want_delete: "",
      add_form_rules: {
        DishName: [{ required: true, message: "必填项", trigger: "blur" }],
        QuantityInStock: [{ required: true, message: "必填项", trigger: "blur" }],
        Description: [{ required: true, message: "必填项", trigger: "blur" }],
        UnitPrice: [{ required: true, message: "必填项", trigger: "blur" }],
      },
      update_form_rules: {
        // 新增更新表单验证规则
        DishName: [{ required: true, message: "必填项", trigger: "blur" }],
        QuantityInStock: [{ required: true, message: "必填项", trigger: "blur" }],
        Description: [{ required: true, message: "必填项", trigger: "blur" }],
        UnitPrice: [{ required: true, message: "必填项", trigger: "blur" }],
      },
    };
  },

  methods: {
    getdata() {
      this.$axios
        .get("/api/manager/dishes", {
          headers: {
            Authorization: localStorage.getItem("token"), // 假设 token 存储在 localStorage 中
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.tableData = res.data.tabledata;
          }
        });
    },
    showdia_add() {
      this.dia_add = true;
    },

    adddish() {
      this.$refs.add_form.validate((valid) => {
        console.log("Validation result:", valid); // 添加调试信息
        if (!valid) return;
        // 验证通过再发送请求
        else {
          this.$axios
            .post("/api/manager/dishes", this.add_form, {
              headers: {
                Authorization: localStorage.getItem("token"), // 确保 token 存储在 localStorage 中
              },
            })
            .then((res) => {
              console.log(res.data);
              if (res.data.status == 200) {
                this.$message({
                  message: "添加成功",
                  type: "success",
                });
                this.dia_add = false;
                this.getdata();
              } else {
                this.$message({
                  message: res.data.msg,
                  type: "error",
                });
              }
            });
        }
      });
    },
    showdia_dlt(row) {
      this.want_delete = row.DishName; // 修改为 DishName
      this.dia_dlt = true;
    },
    deletedish() {
      this.$axios
        .delete("/api/manager/dishes", {
          data: { name: this.want_delete },
          headers: {
            Authorization: localStorage.getItem("token"), // 确保 token 存储在 localStorage 中
          },
        })
        .then((res) => {
          if (res.data.status == 200) {
            this.$message({
              message: res.data.msg,
              type: "success",
            });
            this.getdata();
            this.dia_dlt = false;
          }
        })
        .catch((error) => {
          console.error("Error deleting dish:", error);
          this.$message({
            message: "删除失败，请重试",
            type: "error",
          });
        });
    },
    showdia_update(row) {
      this.update_form.DishID = row.DishID;
      this.update_form.DishName = row.DishName;
      this.update_form.QuantityInStock = row.QuantityInStock;
      this.update_form.Description = row.Description;
      this.update_form.UnitPrice = row.UnitPrice;
      this.dia_update = true;
    },
    updatedish() {
      this.$refs.update_form.validate((valid) => {
        if (!valid) return;
        else {
          this.$axios
            .put("/api/manager/dishes", this.update_form, {
              headers: {
                Authorization: localStorage.getItem("token"),
              },
            })
            .then((res) => {
              if (res.data.status == 200) {
                this.$message({
                  message: "更新成功",
                  type: "success",
                });
                this.dia_update = false;
                this.getdata();
              } else {
                this.$message({
                  message: res.data.message,
                  type: "error",
                });
              }
            })
            .catch((error) => {
              console.error("Error updating dish:", error);
              this.$message({
                message: "更新失败，请重试",
                type: "error",
              });
            });
        }
      });
    },
  },
  computed: {
    uploadHeaders() {
      return {
        Authorization: localStorage.getItem("token"), // 确保 token 存储在 localStorage 中
      };
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
  width: 80%;
  margin: auto;
  margin-top: 30px;
}
</style>
