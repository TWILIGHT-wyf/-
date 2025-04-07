<template>
  <div>
    <div class="header">欢迎点餐</div>
    <div class="body">
      <el-input
        v-model="search"
        placeholder="搜索店铺"
        style="margin-bottom: 20px; width: 300px"
      ></el-input>
      <el-table :data="filteredTableData" style="width: 100%" class="table" border>
        <el-table-column prop="VendorName" label="店铺名称" width="200" align="center">
        </el-table-column>
        <el-table-column prop="VendorAddress" label="店铺地址" width="200" align="center">
        </el-table-column>
        <el-table-column prop="MonthlySales" label="月销量" width="200" align="center">
        </el-table-column>
        <el-table-column prop="operate" label="操作" width="208" align="center">
          <template slot-scope="scope">
            <el-button
              icon="el-icon-plus"
              size="small"
              type="success"
              @click="showdia(scope.row)"
              >订餐
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog title="订餐表单" :visible.sync="dialog" class="dialog" width="60%">
        <div>
          <el-form ref="form" :model="form" label-width="100px">
            <el-form-item label="店铺名称：">
              <span>{{ form.VendorName }}</span>
            </el-form-item>

            <el-form-item label="店铺地址：">
              <span>{{ form.VendorAddress }}</span>
            </el-form-item>

            <el-form-item label="月销量：">
              <span>{{ form.MonthlySales }}</span>
            </el-form-item>

            <!-- 菜品列表 -->
            <el-form-item label="选择菜品：">
              <el-table :data="filteredDishes" style="width: 100%" border>
                <el-table-column
                  prop="DishName"
                  label="菜品名称"
                  width="200"
                  align="center"
                ></el-table-column>
                <el-table-column
                  prop="UnitPrice"
                  label="单价"
                  width="100"
                  align="center"
                ></el-table-column>
                <el-table-column
                  prop="MonthlySales"
                  label="月销量"
                  width="100"
                  align="center"
                ></el-table-column>
                <el-table-column
                  prop="Description"
                  label="菜品简介"
                  width="200"
                  align="center"
                ></el-table-column>
                <el-table-column label="数量" width="150" align="center">
                  <template slot-scope="scope">
                    <el-input-number
                      v-model="scope.row.quantity"
                      :min="0"
                      :max="scope.row.QuantityInStock"
                      label="描述文字"
                    ></el-input-number>
                  </template>
                </el-table-column>
              </el-table>
            </el-form-item>

            <!-- 收餐人信息 -->
            <el-form-item label="客户姓名：">
              <el-input v-model="form.cons_name"></el-input>
            </el-form-item>

            <el-form-item label="送餐地址：">
              <el-input v-model="form.cons_addre"></el-input>
            </el-form-item>
          </el-form>
          <div style="text-align: center">
            <el-button type="primary" @click="add"> 提交 </el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    filteredDishes() {
      return this.dishes.filter((dish) => dish.QuantityInStock > 0);
    },
    filteredTableData() {
      return this.tableData.filter((shop) =>
        shop.VendorName.toLowerCase().includes(this.search.toLowerCase())
      );
    },
  },
  created() {
    this.getdata();
  },
  data() {
    return {
      tableData: [],
      dialog: false,
      search: "", // 添加搜索关键字
      form: {
        VendorName: "",
        VendorAddress: "",
        MonthlySales: "", // 修改为月销量
        cons_name: "",
        cons_addre: "",
      },
      dishes: [],
    };
  },
  methods: {
    getdata() {
      this.$axios
        .get("/api/user/allshops", {
          headers: {
            Authorization: localStorage.getItem("token"),
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.tableData = res.data.tabledata;
          }
        })
        .catch((error) => {
          console.error("Error fetching shops:", error);
        });
    },
    showdia(row) {
      console.log("Row data:", row); // 添加调试信息
      this.form.VendorName = row.VendorName;
      this.form.VendorAddress = row.VendorAddress;
      this.form.MonthlySales = row.MonthlySales; // 修改为月销量

      if (row.VendorID) {
        // 获取当前店铺的菜品列表
        this.$axios
          .get(`/api/user/dishes/${row.VendorID}`)
          .then((res) => {
            console.log("Dishes response:", res.data); // 添加调试信息
            if (res.data.status === 200) {
              this.dishes = res.data.tabledata.map((dish) => ({ ...dish, quantity: 0 }));
            }
          })
          .catch((error) => {
            console.error("Error fetching dishes:", error); // 添加错误处理
            this.$message.error("获取菜品信息失败，请稍后再试");
          });
      } else {
        console.error("VendorID is undefined");
        this.$message.error("店铺ID未定义，请刷新页面后重试");
      }

      this.dialog = true;
    },
    add() {
      const selectedDishes = this.dishes.filter((dish) => dish.quantity > 0);
      const orderData = {
        VendorID: this.tableData.find((shop) => shop.VendorName === this.form.VendorName)
          .VendorID,
        dishes: selectedDishes.map((dish) => ({
          DishID: dish.DishID,
          quantity: dish.quantity,
          UnitPrice: dish.UnitPrice, // 添加单价字段
        })),
        cons_name: this.form.cons_name,
        cons_addre: this.form.cons_addre,
      };

      // 获取 token
      const token = localStorage.getItem("token"); // 假设 token 存储在 localStorage 中

      // 发送请求
      this.$axios
        .post("/api/user/addorder", orderData, {
          headers: {
            Authorization: token,
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status === 200) {
            this.$message({
              message: "成功下单",
              type: "success",
            });
            this.dialog = false;
            this.getdata();
          }
        })
        .catch((error) => {
          console.error("Error adding order:", error);
          this.$message.error("下单失败，请稍后再试");
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
  width: 62%;
  margin: auto;
  margin-top: 30px;
}

.dialog {
}
</style>
